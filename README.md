# cognito-user-shell
## Extendable Python shell/CLI tool/API client with AWS Cognito authentication
Example package shows how you can expand and implement your own tools.

### Installation
`pip install cognito-user-shell`

### Run the example
```bash
git clone https://github.com/jussiniinikoski/cognito-user-shell.git
cd cognito-user-shell
# Set up some environment variables
# set PYTHONPATH to current directory if didn't pip install
export PYTHONPATH=./
export COGNITO_CLIENT_ID=add-your-aws-cognito-client-id-here
export API_URL=http://127.0.0.1:8000
python example
```
