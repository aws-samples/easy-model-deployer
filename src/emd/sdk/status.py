import boto3
from typing import Dict, List, Optional, Tuple
import concurrent.futures
import time
from functools import lru_cache

from emd.constants import CODEPIPELINE_NAME, MODEL_DEFAULT_TAG
from emd.utils.aws_service_utils import (
    check_stack_status,
    get_pipeline_active_executions,
    get_model_stacks,
    check_env_stack_exist_and_complete,
    get_current_region
)
from emd.utils.logger_utils import get_logger

# Constants
PARALLEL_EXECUTION_SEPARATOR = "__"
MAX_PARALLEL_EXECUTIONS_PER_MODEL = 5
PARALLEL_API_TIMEOUT = 60  # seconds

# Pipeline execution retry configuration for AWS eventual consistency
PIPELINE_EXECUTION_RETRY_MAX_ATTEMPTS = 5
PIPELINE_EXECUTION_RETRY_INITIAL_DELAY = 2.0  # seconds
PIPELINE_EXECUTION_RETRY_MAX_DELAY = 30.0     # seconds
PIPELINE_EXECUTION_RETRY_BACKOFF_FACTOR = 2.0

logger = get_logger(__name__)


class StatusError(Exception):
    """Base exception for status-related errors"""
    pass


class PipelineStatusError(StatusError):
    """Exception raised when pipeline status cannot be retrieved"""
    pass


class StackStatusError(StatusError):
    """Exception raised when stack status cannot be retrieved"""
    pass


def get_pipeline_execution_status(
    pipeline_execution_id: str,
    pipeline_name: str = CODEPIPELINE_NAME,
    region: Optional[str] = None
) -> Dict:
    """
    Get detailed status information for a specific pipeline execution.

    Args:
        pipeline_execution_id: The unique identifier for the pipeline execution
        pipeline_name: Name of the CodePipeline (defaults to CODEPIPELINE_NAME)
        region: AWS region (defaults to current region)

    Returns:
        Dict containing execution status, stage information, and metadata

    Raises:
        PipelineStatusError: If pipeline execution cannot be found or accessed
    """
    if region is None:
        region = get_current_region()

    try:
        client = boto3.client('codepipeline', region_name=region)

        response = client.get_pipeline_execution(
            pipelineName=pipeline_name,
            pipelineExecutionId=pipeline_execution_id
        )

        execution = response['pipelineExecution']
        status = execution['status']
        status_summary = execution.get('statusSummary', "")
        result = {
            "status": status,
            "status_code": 1 if status not in ['Stopped', 'Succeeded', 'Cancelled', "Failed"] else 0,
            "is_succeeded": status == 'Succeeded',
            "stage_name": None,
            "status_summary": status_summary,
            "pipeline_execution_id": pipeline_execution_id
        }

        # Get current stage information - IMPROVED APPROACH
        try:
            # First try the new action-based approach (works for all execution states)
            stage_name = _find_stage_for_execution_via_actions(
                pipeline_name, pipeline_execution_id, client
            )

            # If action-based approach fails, try pipeline state approach (for active executions)
            if stage_name == "Unknown":
                logger.debug(f"Action-based stage detection returned 'Unknown' for {pipeline_execution_id}, trying pipeline state")

                pipeline_state = client.get_pipeline_state(name=pipeline_name)
                stage_name = _find_stage_for_execution(pipeline_state, pipeline_execution_id)

            # If both approaches fail, fall back to original method
            if stage_name == "Unknown":
                logger.debug(f"All direct methods failed for {pipeline_execution_id}, falling back to get_pipeline_active_executions")

                active_executions = get_pipeline_active_executions(
                    pipeline_name=pipeline_name,
                    client=client,
                    return_dict=True,
                    filter_stoped=False,
                    filter_failed=False
                )

                if pipeline_execution_id in active_executions:
                    execution_info = active_executions[pipeline_execution_id]
                    result.update({
                        'stage_name': execution_info['stage_name'],
                        'model_id': execution_info['model_id'],
                        'model_tag': execution_info['model_tag'],
                        'instance_type': execution_info['instance_type'],
                        'engine_type': execution_info['engine_type'],
                        'service_type': execution_info['service_type']
                    })
                    logger.debug(f"Fallback method found stage: {execution_info['stage_name']}")
                    return result
                else:
                    result['stage_name'] = "Unknown"
                    logger.warning(f"Execution {pipeline_execution_id} not found in any method")
                    return result

            # We found the stage name, now set it
            result.update({
                'stage_name': stage_name,
            })
            logger.debug(f"Found stage: {stage_name}")

            # Try to get additional execution details from active executions
            try:
                active_executions = get_pipeline_active_executions(
                    pipeline_name=pipeline_name,
                    client=client,
                    return_dict=True,
                    filter_stoped=False,
                    filter_failed=False
                )

                if pipeline_execution_id in active_executions:
                    execution_info = active_executions[pipeline_execution_id]
                    result.update({
                        'model_id': execution_info['model_id'],
                        'model_tag': execution_info['model_tag'],
                        'instance_type': execution_info['instance_type'],
                        'engine_type': execution_info['engine_type'],
                        'service_type': execution_info['service_type']
                    })
            except Exception as e:
                logger.debug(f"Could not get additional execution details for {pipeline_execution_id}: {e}")

        except Exception as e:
            logger.warning(f"Could not get stage info for execution {pipeline_execution_id}: {e}")
            result['stage_name'] = f"Error getting stage info: {str(e)}"

        return result

    except client.exceptions.PipelineExecutionNotFoundException:
        return {
            "status": "NotFound",
            "status_code": 1,  # FIXED: Keep monitoring instead of exiting
            "is_succeeded": False,
            "stage_name": None,
            "status_summary": "Pipeline execution not found (eventual consistency delay)",
            "pipeline_execution_id": pipeline_execution_id
        }
    except Exception as e:
        logger.error(f"Error getting pipeline execution status: {e}")
        raise PipelineStatusError(f"Failed to get pipeline execution status: {e}")


def get_pipeline_execution_status_with_retry(
    pipeline_execution_id: str,
    pipeline_name: str = CODEPIPELINE_NAME,
    region: Optional[str] = None,
    max_retries: int = PIPELINE_EXECUTION_RETRY_MAX_ATTEMPTS,
    initial_delay: float = PIPELINE_EXECUTION_RETRY_INITIAL_DELAY
) -> Dict:
    """
    Get pipeline execution status with retry logic for AWS eventual consistency.

    This function handles the common case where pipeline execution is created but not immediately
    queryable due to AWS distributed system delays. It implements exponential backoff with jitter
    to handle temporary API failures gracefully.

    Args:
        pipeline_execution_id: The unique identifier for the pipeline execution
        pipeline_name: Name of the CodePipeline (defaults to CODEPIPELINE_NAME)
        region: AWS region (defaults to current region)
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds

    Returns:
        Dict containing execution status, stage information, and metadata

    Raises:
        PipelineStatusError: If pipeline execution cannot be found after all retries
    """
    import time
    import random

    if region is None:
        region = get_current_region()

    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            # Try the original function
            return get_pipeline_execution_status(pipeline_execution_id, pipeline_name, region)

        except Exception as e:
            last_exception = e

            # Check if it's the expected "not found" exception and we have retries left
            if (hasattr(e, 'response') and
                e.response.get('Error', {}).get('Code') == 'PipelineExecutionNotFoundException' and
                attempt < max_retries):

                # Add jitter to prevent thundering herd problem
                jitter = random.uniform(0.1, 0.5)
                sleep_time = delay + jitter

                logger.debug(f"Pipeline execution {pipeline_execution_id} not found, retrying in {sleep_time:.1f}s (attempt {attempt + 1}/{max_retries + 1})")
                time.sleep(sleep_time)

                # Exponential backoff with maximum cap
                delay = min(delay * PIPELINE_EXECUTION_RETRY_BACKOFF_FACTOR, PIPELINE_EXECUTION_RETRY_MAX_DELAY)
                continue
            else:
                # Re-raise if it's not the expected exception or we're out of retries
                raise

    # If we get here, all retries failed
    logger.warning(f"All {max_retries} retries failed for pipeline execution {pipeline_execution_id}")
    raise last_exception


def get_destroy_status(stack_name: str) -> Dict:
    """
    Get the destruction status of a CloudFormation stack.

    Args:
        stack_name: Name of the CloudFormation stack

    Returns:
        Dict containing destruction status and success indicator

    Raises:
        StackStatusError: If stack status cannot be determined
    """
    try:
        stack_status = check_stack_status(stack_name)
        status = stack_status.status

        if not stack_status.is_exist:
            return {
                "status_code": 0,
                "status": status,
                "is_succeeded": True
            }

        if status == "DELETE_FAILED":
            return {
                "status_code": 0,
                "is_succeeded": False,
                "status": status,
            }

        return {
            "status_code": 1,
            "is_succeeded": False,
            "status": status,
        }

    except Exception as e:
        logger.error(f"Error getting destroy status for stack {stack_name}: {e}")
        raise StackStatusError(f"Failed to get destroy status: {e}")


def get_model_status(model_id: Optional[str] = None, model_tag: str = MODEL_DEFAULT_TAG) -> Dict:
    """
    Get comprehensive status of model deployments with enhanced pipeline-stack logic.

    This function provides real-time status information for model deployments by:
    1. Fetching pipeline executions and CloudFormation stacks in parallel
    2. Applying enhanced pipeline-stack status logic to filter and enrich results
    3. Organizing results by in-progress and completed deployments

    Args:
        model_id: Specific model ID to filter by. If None, returns all models
        model_tag: Model tag to filter by

    Returns:
        Dict with 'inprogress' and 'completed' keys containing model information:
        - 'inprogress': List of active pipeline executions (with enhanced status logic)
        - 'completed': List of completed CloudFormation stacks

    Raises:
        StatusError: If status information cannot be retrieved
    """
    try:
        check_env_stack_exist_and_complete()

        start_time = time.time()

        # Parallel data fetching for optimal performance
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both AWS API calls simultaneously
            pipeline_future = executor.submit(
                get_pipeline_active_executions,
                pipeline_name=CODEPIPELINE_NAME,
                filter_stoped=False,
                filter_failed=False
            )
            stacks_future = executor.submit(get_model_stacks)

            # Wait for both results with timeout
            try:
                active_executions = pipeline_future.result(timeout=PARALLEL_API_TIMEOUT)
                model_stacks = stacks_future.result(timeout=PARALLEL_API_TIMEOUT)
            except concurrent.futures.TimeoutError:
                logger.error("Timeout waiting for AWS API responses")
                raise StatusError("Timeout retrieving status information")

        logger.debug(f"Parallel data fetch completed in {time.time() - start_time:.2f}s")

        # Apply enhanced pipeline-stack status logic
        enhanced_executions = _apply_enhanced_pipeline_stack_logic(active_executions)

        # Filter out invalid executions (now includes pipeline-stack logic filtering)
        filtered_executions = _filter_valid_executions(enhanced_executions)

        # Organize results
        result = {
            "inprogress": [],
            "completed": []
        }

        if model_id is not None:
            # Filter for specific model
            result['inprogress'] = _filter_executions_by_model(
                filtered_executions, model_id, model_tag
            )
            result['completed'] = _filter_stacks_by_model(
                model_stacks, model_id, model_tag
            )
        else:
            # Return all models
            result['inprogress'] = filtered_executions
            result['completed'] = model_stacks

        logger.debug(f"Total status processing time: {time.time() - start_time:.2f}s")
        return result

    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise StatusError(f"Failed to get model status: {e}")


def get_parallel_executions_for_model(
    model_id: str,
    model_tag: str = MODEL_DEFAULT_TAG
) -> List[Dict]:
    """
    Get all parallel executions for a specific model+tag combination.

    Useful for monitoring multiple concurrent deployments of the same model.

    Args:
        model_id: The model identifier
        model_tag: The model tag

    Returns:
        List of execution information dictionaries

    Raises:
        StatusError: If execution information cannot be retrieved
    """
    try:
        check_env_stack_exist_and_complete()

        start_time = time.time()

        # Optimized single API call
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            pipeline_future = executor.submit(
                get_pipeline_active_executions,
                pipeline_name=CODEPIPELINE_NAME,
                filter_stoped=False,
                filter_failed=False
            )
            active_executions = pipeline_future.result(timeout=PARALLEL_API_TIMEOUT)

        logger.debug(f"Pipeline data fetch completed in {time.time() - start_time:.2f}s")

        # Filter for specific model
        model_key = f"{model_id}__{model_tag}"
        parallel_executions = []

        for execution_info in active_executions:
            execution_model_key = f"{execution_info['model_id']}__{execution_info['model_tag']}"
            if execution_model_key == model_key:
                parallel_executions.append(execution_info)

        return parallel_executions

    except Exception as e:
        logger.error(f"Error getting parallel executions for model {model_id}: {e}")
        raise StatusError(f"Failed to get parallel executions: {e}")


def get_execution_summary() -> Dict:
    """
    Get a summary of all executions grouped by model.

    Provides a comprehensive view of all model deployments organized by model+tag
    for better visibility in parallel deployment scenarios.

    Returns:
        Dict with model keys containing execution summaries

    Raises:
        StatusError: If execution summary cannot be generated
    """
    try:
        check_env_stack_exist_and_complete()

        start_time = time.time()

        # Optimized single API call
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            pipeline_future = executor.submit(
                get_pipeline_active_executions,
                pipeline_name=CODEPIPELINE_NAME,
                filter_stoped=False,
                filter_failed=False
            )
            active_executions = pipeline_future.result(timeout=PARALLEL_API_TIMEOUT)

        logger.debug(f"Pipeline data fetch completed in {time.time() - start_time:.2f}s")

        # Group executions by model+tag
        executions_by_model = {}
        for execution_info in active_executions:
            model_key = f"{execution_info['model_id']}__{execution_info['model_tag']}"

            if model_key not in executions_by_model:
                executions_by_model[model_key] = {
                    'model_id': execution_info['model_id'],
                    'model_tag': execution_info['model_tag'],
                    'executions': []
                }

            executions_by_model[model_key]['executions'].append({
                'pipeline_execution_id': execution_info['pipeline_execution_id'],
                'status': execution_info['status'],
                'stage_name': execution_info['stage_name'],
                'instance_type': execution_info['instance_type'],
                'engine_type': execution_info['engine_type'],
                'service_type': execution_info['service_type'],
                'create_time': execution_info['create_time']
            })

        return executions_by_model

    except Exception as e:
        logger.error(f"Error getting execution summary: {e}")
        raise StatusError(f"Failed to get execution summary: {e}")


def validate_parallel_execution_limit(
    model_id: str,
    model_tag: str = MODEL_DEFAULT_TAG
) -> Tuple[bool, str]:
    """
    Validate that parallel execution limits are not exceeded.

    Prevents resource exhaustion by enforcing reasonable limits on
    concurrent deployments of the same model.

    Args:
        model_id: The model identifier
        model_tag: The model tag

    Returns:
        Tuple of (is_valid, message) indicating if deployment is allowed

    Raises:
        StatusError: If validation cannot be performed
    """
    try:
        parallel_executions = get_parallel_executions_for_model(model_id, model_tag)
        current_count = len(parallel_executions)

        if current_count >= MAX_PARALLEL_EXECUTIONS_PER_MODEL:
            return False, (
                f"Maximum parallel executions ({MAX_PARALLEL_EXECUTIONS_PER_MODEL}) "
                f"reached for model {model_id} (tag: {model_tag}). "
                f"Current: {current_count}"
            )

        return True, (
            f"Parallel execution allowed. "
            f"Current count: {current_count}/{MAX_PARALLEL_EXECUTIONS_PER_MODEL}"
        )

    except Exception as e:
        logger.error(f"Error validating parallel execution limit: {e}")
        raise StatusError(f"Failed to validate execution limit: {e}")


# Private helper functions

def _is_execution_over_24_hours(create_time_str: str) -> bool:
    """
    Check if an execution is over 24 hours old based on its create_time string.

    Args:
        create_time_str: Create time string in format "YYYY-MM-DD HH:MM:SS UTC"

    Returns:
        bool: True if execution is over 24 hours old, False otherwise
    """
    try:
        import datetime
        from datetime import timezone

        # Parse the create time string (format: "2025-07-28 13:47:04 UTC")
        create_time = datetime.datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S %Z")
        create_time = create_time.replace(tzinfo=timezone.utc)

        # Get current time
        current_time = datetime.datetime.now(timezone.utc)

        # Calculate time difference
        time_diff = current_time - create_time

        # Check if over 24 hours (24 * 60 * 60 = 86400 seconds)
        # Use >= to include exactly 24 hours as "over 24 hours"
        return time_diff.total_seconds() >= 86400

    except Exception as e:
        logger.warning(f"Error parsing create time '{create_time_str}': {e}")
        # On error, assume it's not over 24 hours to avoid excluding valid executions
        return False


def _apply_enhanced_pipeline_stack_logic(executions: List[Dict]) -> List[Dict]:
    """
    Apply enhanced pipeline-stack status logic to filter and enrich executions.

    This implements the comprehensive logic for handling pipeline and CloudFormation
    stack relationships with optimized batch stack checking.
    """
    from emd.utils.aws_service_utils import batch_check_stack_status
    from emd.constants import MODEL_STACK_NAME_PREFIX

    enhanced_executions = []

    # Step 1: Pre-filter executions and collect stack names for batch checking
    failed_deploy_executions = []
    succeeded_executions = []
    stack_names_to_check = []

    for execution_info in executions:
        pipeline_status = execution_info.get('status', '')
        stage_name = execution_info.get('stage_name', '')
        model_id = execution_info.get('model_id', '')
        model_tag = execution_info.get('model_tag', '')

        # Generate stack name (same logic as in deployment)
        stack_name = f"{MODEL_STACK_NAME_PREFIX}{model_id.lower().replace('.', '-').replace('_', '-')}-{model_tag}"
        execution_info['_stack_name'] = stack_name  # Store for later use

        # Case 1: Pipeline Failed + Stage = Deploy - needs stack check
        if pipeline_status == 'Failed' and stage_name == 'Deploy':
            failed_deploy_executions.append(execution_info)
            stack_names_to_check.append(stack_name)

        # Case 2: Pipeline Failed + Stage = Source/Build - check 24h filter
        elif pipeline_status == 'Failed' and stage_name in ['Source', 'Build']:
            create_time_str = execution_info.get('create_time', '')
            if create_time_str and _is_execution_over_24_hours(create_time_str):
                # Exclude executions over 24 hours old
                logger.debug(f"Excluding Failed {stage_name} execution {execution_info.get('pipeline_execution_id')} - over 24 hours old")
                continue
            else:
                # Include with CLI message flag
                execution_info['enhanced_status'] = f'Failed ({stage_name})'
                execution_info['cli_message'] = 'codepipeline_console'
                enhanced_executions.append(execution_info)

        # Case 3: Pipeline Succeeded - needs stack check
        elif pipeline_status == 'Succeeded':
            succeeded_executions.append(execution_info)
            stack_names_to_check.append(stack_name)

        # Case 4: Pipeline InProgress (always include, no stack check)
        elif pipeline_status == 'InProgress':
            enhanced_executions.append(execution_info)

        # Default case: include other statuses
        else:
            enhanced_executions.append(execution_info)

    # Step 2: Batch check all required stacks in a single API call
    stack_statuses = {}
    if stack_names_to_check:
        logger.debug(f"Batch checking {len(set(stack_names_to_check))} unique stacks")
        stack_statuses = batch_check_stack_status(list(set(stack_names_to_check)))

    # Step 3: Process Failed Deploy executions with batch results
    for execution_info in failed_deploy_executions:
        stack_name = execution_info['_stack_name']
        stack_status = stack_statuses.get(stack_name)

        if stack_status and stack_status.is_exist and 'ROLLBACK' in stack_status.status:
            # Include with enhanced status and CLI message flag
            execution_info['enhanced_status'] = f'Failed (Deploy - Stack {stack_status.status})'
            execution_info['cli_message'] = 'cleanup_warning'
            execution_info['stack_name'] = stack_name
            enhanced_executions.append(execution_info)
        else:
            # Exclude from response (stack not found or not in rollback state)
            logger.debug(f"Excluding Failed Deploy execution {execution_info.get('pipeline_execution_id')} - stack not found or not in rollback")

    # Step 4: Process Succeeded executions with batch results
    for execution_info in succeeded_executions:
        stack_name = execution_info['_stack_name']
        stack_status = stack_statuses.get(stack_name)

        if stack_status and stack_status.is_exist:
            # Include in response (normal case)
            enhanced_executions.append(execution_info)
        else:
            # Exclude from response (user manually deleted stack)
            logger.debug(f"Excluding Succeeded execution {execution_info.get('pipeline_execution_id')} - stack manually deleted")

    # Clean up temporary stack name field
    for execution_info in enhanced_executions:
        execution_info.pop('_stack_name', None)

    logger.debug(f"Enhanced pipeline-stack logic: {len(executions)} → {len(enhanced_executions)} executions")
    logger.debug(f"Batch checked {len(stack_statuses)} stacks in single API call")
    return enhanced_executions


def _filter_valid_executions(executions: List[Dict]) -> List[Dict]:
    """Filter out invalid executions (Failed with Unknown stage and other invalid states)"""
    filtered_executions = []

    for execution_info in executions:
        execution_status = execution_info.get('status', '')
        stage_name = execution_info.get('stage_name', '')

        # Skip executions with 'Failed (Unknown)' status (legacy filtering)
        if execution_status == 'Failed' and stage_name == 'Unknown':
            continue

        filtered_executions.append(execution_info)

    return filtered_executions


def _filter_executions_by_model(
    executions: List[Dict],
    model_id: str,
    model_tag: str
) -> List[Dict]:
    """Filter executions for a specific model+tag combination"""
    filtered_executions = []

    for execution_info in executions:
        if (execution_info['model_id'] == model_id and
            execution_info['model_tag'] == model_tag):
            filtered_executions.append(execution_info)

    return filtered_executions


def _filter_stacks_by_model(
    stacks: List[Dict],
    model_id: str,
    model_tag: str
) -> List[Dict]:
    """Filter stacks for a specific model+tag combination"""
    filtered_stacks = []

    for stack_info in stacks:
        if (stack_info['model_id'] == model_id and
            stack_info['model_tag'] == model_tag):
            filtered_stacks.append(stack_info)

    return filtered_stacks


def _find_stage_for_execution_via_actions(pipeline_name: str, execution_id: str, client) -> str:
    """
    Find the current/failed stage for a specific pipeline execution using list_action_executions.

    This method works for all execution states (InProgress, Failed, Succeeded) unlike get_pipeline_state
    which only shows currently active stages.

    Args:
        pipeline_name: Name of the CodePipeline
        execution_id: The pipeline execution ID to find the stage for
        client: boto3 CodePipeline client

    Returns:
        str: The stage name where the execution is currently running or failed, or "Unknown" if not found
    """
    try:
        response = client.list_action_executions(
            pipelineName=pipeline_name,
            filter={
                'pipelineExecutionId': execution_id
            }
        )

        action_executions = response.get('actionExecutionDetails', [])
        logger.debug(f"Found {len(action_executions)} action executions for {execution_id}")

        if not action_executions:
            return "Unknown"

        # Find the stage where execution is currently running or failed
        current_stage = "Unknown"

        # Look for failed or in-progress actions first (these indicate current stage)
        for action_exec in action_executions:
            stage_name = action_exec.get('stageName', 'Unknown')
            status = action_exec.get('status', 'Unknown')
            action_name = action_exec.get('actionName', 'Unknown')

            logger.debug(f"Action: {action_name}, Stage: {stage_name}, Status: {status}")

            # If we find a failed or in-progress action, that's the current stage
            if status in ['Failed', 'InProgress', 'Stopping']:
                current_stage = stage_name
                logger.debug(f"Found current/failed stage: {stage_name} (status: {status})")
                break

        # If no failed/in-progress actions, find the last stage (for completed executions)
        if current_stage == "Unknown" and action_executions:
            # Get all unique stages and find the last one in pipeline order
            stages_found = []
            for action_exec in action_executions:
                stage_name = action_exec.get('stageName', 'Unknown')
                if stage_name not in stages_found:
                    stages_found.append(stage_name)

            # For completed executions, return the last stage
            if stages_found:
                current_stage = stages_found[-1]  # Last stage in the list
                logger.debug(f"Execution completed, using last stage: {current_stage}")

        return current_stage

    except Exception as e:
        logger.warning(f"Error getting stage via action executions for {execution_id}: {e}")
        return "Unknown"


def _find_stage_for_execution(pipeline_state: dict, execution_id: str) -> str:
    """
    Find the current stage for a specific pipeline execution using pipeline state.

    This is the legacy method that only works for currently active executions.

    Args:
        pipeline_state: The pipeline state response from get_pipeline_state API
        execution_id: The pipeline execution ID to find the stage for

    Returns:
        str: The stage name where the execution is currently running, or "Unknown" if not found
    """
    stage_states = pipeline_state.get("stageStates", [])

    # Debug logging
    logger.debug(f"Looking for execution {execution_id} in {len(stage_states)} stages via pipeline state")

    # Find current stage for this execution
    current_stage = "Unknown"
    for stage_state in stage_states:
        stage_name = stage_state.get("stageName", "UnknownStage")
        stage_execution_ids = []

        # Check inbound executions
        inbound_executions = stage_state.get("inboundExecutions", [])
        for d in inbound_executions:
            if isinstance(d, dict) and "pipelineExecutionId" in d:
                stage_execution_ids.append(d["pipelineExecutionId"])

        # Check latest execution
        latest_execution = stage_state.get("latestExecution", {})
        if latest_execution and latest_execution.get("pipelineExecutionId"):
            stage_execution_ids.append(latest_execution["pipelineExecutionId"])

        # Check action states for parallel executions
        for action_state in stage_state.get("actionStates", []):
            latest_action = action_state.get("latestExecution", {})
            if latest_action and latest_action.get("pipelineExecutionId"):
                stage_execution_ids.append(latest_action["pipelineExecutionId"])

            # Also check current execution in action state
            current_execution = action_state.get("currentRevision", {})
            if current_execution and current_execution.get("pipelineExecutionId"):
                stage_execution_ids.append(current_execution["pipelineExecutionId"])

        # Debug logging for each stage
        logger.debug(f"Stage '{stage_name}' has execution IDs: {stage_execution_ids}")

        if execution_id in stage_execution_ids:
            current_stage = stage_name
            logger.debug(f"Found execution {execution_id} in stage '{stage_name}' via pipeline state")
            break

    if current_stage == "Unknown":
        logger.debug(f"Execution {execution_id} not found in pipeline state, will try action executions")

    return current_stage
