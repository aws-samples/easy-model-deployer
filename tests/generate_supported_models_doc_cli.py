import argparse
import pandas
from emd.models import Model


def generate_model_table():
    model_infos = []
    for _, model in Model.model_map.items():
        supported_instances = [i.instance_type for i in model.supported_instances]
        if "local" in supported_instances:
            supported_instances.remove("local")
        supported_services = [s.service_type for s in model.supported_services]
        if "local" in supported_services:
            supported_services.remove("local")

        suport_cn_region = "✅" if model.allow_china_region else "❎"
        model_infos.append({
            "ModeId": model.model_id,
            "ModelSeries": model.model_series.model_series_name,
            "ModelType": model.model_type,
            "Supported Engines": ",".join([e.engine_type for e in model.supported_engines]),
            "Supported Instances": ",".join(supported_instances),
            "Supported Services": ",".join(supported_services),
            "Support China Region": suport_cn_region,
        })

    df = pandas.DataFrame(model_infos)
    return str(df.to_markdown(index=False))



def main():
    parser = argparse.ArgumentParser(description='Generate model documentation table')
    parser.add_argument('-o', '--output',default="docs/en/supported_models.md",
                      help='Output file path. If not specified, prints to stdout')

    args = parser.parse_args()

    table = generate_model_table()

    if args.output:
        with open(args.output, 'w') as f:
            f.write(table)
    else:
        print(table)


if __name__ == '__main__':
    main()
