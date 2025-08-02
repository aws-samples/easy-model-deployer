<style>
.md-content__inner {
    padding: 0 !important;
    margin: 0 !important;
    height: 100% !important;
    border: none !important;
    outline: none !important;
}
.md-content {
    padding: 0 !important;
    margin: 0 !important;
    height: 100% !important;
    border: none !important;
    outline: none !important;
}
.md-main__inner {
    padding: 0 !important;
    margin: 0 !important;
    height: 100% !important;
    border: none !important;
    outline: none !important;
}
.md-grid {
    max-width: none !important;
    margin: 0 !important;
    height: 100% !important;
    border: none !important;
    outline: none !important;
}
.md-main {
    height: 100% !important;
    border: none !important;
    outline: none !important;
}
#modelGeneratorFrame {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    -webkit-box-shadow: none !important;
    -moz-box-shadow: none !important;
}
</style>

<iframe id="modelGeneratorFrame" src="model-generator.html" width="100%" height="100%" frameborder="0" style="border: none; display: block; margin: 0; padding: 0; min-height: calc(100vh - 120px);"></iframe>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Find .wy-nav-content and remove padding and max-width
    const wyNavContent = document.querySelector('.wy-nav-content');
    if (wyNavContent) {
        wyNavContent.style.padding = '0';
        wyNavContent.style.maxWidth = 'none';
    }

    // Find hr element under ul.wy-breadcrumbs and remove it
    const wyBreadcrumbs = document.querySelector('ul.wy-breadcrumbs');
    if (wyBreadcrumbs) {
        const hrElement = wyBreadcrumbs.nextElementSibling;
        if (hrElement && hrElement.tagName === 'HR') {
            hrElement.remove();
        }
    }
});
</script>
