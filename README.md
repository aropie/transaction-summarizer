# Transaction Summarizer

This project lets you upload a transactions csv file via a HTTP
request. That file is then processed, the transactions are inserted
into a DB and finally, a summary email is sent to previously configured
email address.

The project runs as a Lambda on AWS and is
automatically provisioned by use of Terraform, so that it can be
deployed with ease. It also provisions a PostgreSQL RDS instance by
default, but can be configured to use an already existing one.

## The CSV transactions file
The CSV transactions file should contain a single transaction per row
and have the following format:

| id | date       | transaction |
|:--:|:----------:|:-----------:|
| 1  | 2021/07/09 | -60.5       |
| 2  | 2022/07/10 | +60.5       |
| 8  | 2023/10/14 | +42.2       |
| 4  | 2023/10/26 | -12         |

Details to take into account:
- The `id` field **must** be positive integers, but they **do not
  need** to be in order.
- The `date` field **must** be in [ISO
  8601](https://en.wikipedia.org/wiki/ISO_8601) format with forward
  slashes (YYYY/MM/DD).
- The `transaction` field **must** be a decimal number and can be
  negative, positive or zero. For the purpose of this project,
  positive values are interpreted as credit transactions and negative
  values as debit transactions.

## Running locally
Beforehand, you [should adjust the settings and
variables](#configuring-settings-and-variables) to your preferences,
specially the parameters to connect to the DB and the credentials for
the SMTP server. First, create a virtual environment and install the dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```
Then, you can run the project:
```bash
python -m src.app input.csv
```
You should get a message saying that the csv file was processed successfully and the
subsequent email has been sent.

### Important note about the processing of the file
The transactions file is assumed to be an additive source of truth for
the transactions.  Also, the `id` for a transaction is treated as a
unique identifier (by definition).  This means that if a given
transaction file was sent with two transactions having the same `id`
but different `date` or `value`, then the newest transaction will
overwrite the previous one. This also applies if two files are sent
one after the other with transactions with the same `id` having
different `date` or `value`; the transaction with that `id` will
always be updated to the last known value.

## Configuring settings and variables
This project makes use of [Dynaconf](https://www.dynaconf.com/) for
its settings files, so there are two places to look at:
`settings.toml` and `.secrets.toml`. You can take a look at
`settings.toml` for the configurable settings available and for
setting the required credentials for connecting to both the DB and the
SMTP server for the email sending. `.secrets.toml` is intended for
sensible values (like the DB password) and **should not be version-controlled**.

### For Gmail users
Prior to May 30, 2022, it was possible to connect to Gmail’s SMTP
server using your regular Gmail password if "2-step verification" was
activated.  For a higher security standard, Google now requires you to
use an “App Password“. This is a 16-digit passcode that is generated
in your Google account and allows less secure apps or devices that
don’t support 2-step verification to sign in to your Gmail Account
[(official docs)](https://support.google.com/accounts/answer/185833?hl=en).


## Deploying to AWS
The project assumes you have an already [configured AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html)
available. Also, you [should adjust the settings and variables](#configuring-settings-and-variables)
to your preferences. To deploy the project:
```bash
cd terraform
terraform init
```
This will download and setup all required Terraform resources. Then apply the configuration
to make the actual deploy
```bash
# in terraform/
terraform apply
```

You can then see the provisioned URL for your instance with
```bash
terraform output api_url
```

> If using the provisioned DB, you might need to first do the full deployment
> in order to get the DB hostname, set the db_hostname in `.secrets.toml` and then re-deploy.
> You can get the DB's hostname with `terraform output db_hostname`.

Each time you run `terraform apply`, you will be asked for the values of the variables
that Terraform requires in order to make the deployment. For ease of use, you can supply
said variables with using a file with the `-var-file` flag:
```bash
terraform apply -var-file=dev.tfvars
```
An example of such file can be found in `terraform/variables/dev.tfvars`.


## Sending the transactions file via request
Once terraform lets you know that everything was successfully
deployed, you should now be able to send the [transactions file](#the-csv-transactions-file).
The deployed Lambda will be listening for a POST at the `/upload`
endpoint and the file needs to be sent within a `multipart/form-data`
request. It does not matter the name of the file but it must be sent
with the `file` parameter.

An example of a request with curl:
```bash
# in terraform/ so that terraform can find the output
curl --location $(terraform output -raw api_url)/upload \
--form 'file=@"../input.csv"'
```

You should receive a status code 200 with a message saying that the
file was processed correctly.  The email should also have been sent
with the formatted transaction summary. The email gets sent both as
HTML and as plain text to enable email clients that don't support HTML
and users that only want to receive plain text.

Additionally, if the DB was also provisioned with Terraform, you can now connect to the DB
to see the transactions inserted:
```bash
psql -h $(terraform output -raw rds_hostname) \
-p $(terraform output -raw rds_port) \
-U $(terraform output -raw rds_username) $(terraform output -raw rds_database)
```
## Future development
- Get the target email as a parameter of the request.
- Add authentication
- Support for multiple accounts.
- Boolean flag to configure if the summary email should be sent or just process the transactions file.
