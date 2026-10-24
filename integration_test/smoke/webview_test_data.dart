// Shared local content for native WebView smoke and the release probe.
const webViewReadyText = 'REV142 WebView release OK';
const rev142WebViewHtml =
    '''
<!doctype html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>REV142 local WebView</title>
<style>body { padding: 24px; font: 20px sans-serif; background: #fff9ec; }</style>
</head><body>
<h1 id="status">Loading local page...</h1><p>Local HTML and JavaScript.</p>
<script>document.getElementById('status').textContent = '$webViewReadyText';</script>
</body></html>
''';
