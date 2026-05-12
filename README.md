# ride-surge-predictor


## Installation
Requirements: Ollama installed + qwen3.5:2b model.

Clone the repo.
`chmod +x REPOPATH/src/collection/host.py`
### Setting up extension
#### Native Host
##### Mozilla

```json
{
  "name": "com.nil.browser_control",
  "description": "Python Native Bridge",
  "path": "REPOPATH/src/collection/host.py",
  "type": "stdio",
  "allowed_extensions": [
    "control@nil.com"
  ]
}
```
(Place this JSON file in `~/.mozilla/native-messaging-hosts/com.nil.browser_control.json`. Remember to adjust the path value.)

##### Chrome
Open Chrome and go to chrome://extensions/

Turn on Developer mode (top right).

Click Load unpacked and select your extension folder.

Copy the generated ID (it looks like abcdefghijklmnopqrstuvwxyzabcdef).
```json
{
  "name": "com.nil.browser_control",
  "description": "Python Native Bridge",
  "path": "REPOPATH/src/collection/host.py",
  "type": "stdio",
  "allowed_origins":[
    "chrome-extension://<PASTE_YOUR_EXTENSION_ID_HERE>/"
  ]
}
```
(Place this JSON file in `~/.config/google-chrome/NativeMessagingHosts/com.nil.browser_control.json` for Chrome or `~/.config/chromium/NativeMessagingHosts/com.nil.browser_control.json` for Chromium. Remember to adjust the path value.)