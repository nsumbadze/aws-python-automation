import logging
import mimetypes
from os import getenv
from pathlib import Path

from botocore.exceptions import ClientError

from common.auth import init_s3_client
from s3.host_static_site.my_args import build_parser


PUBLIC_READ_POLICY = """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::%s/*"
    }
  ]
}"""


def generate_index_html(first_name: str, last_name: str) -> str:
    full_name = f"{first_name} {last_name}"
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{full_name}</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f4f1ea;
        --text: #1f1a17;
        --accent: #b25b2a;
      }}
      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, #f4f1ea 0%, #e8dcc8 100%);
        font-family: Georgia, "Times New Roman", serif;
        color: var(--text);
      }}
      main {{
        padding: 3rem;
        border: 1px solid rgba(31, 26, 23, 0.12);
        background: rgba(255, 255, 255, 0.72);
        box-shadow: 0 20px 50px rgba(31, 26, 23, 0.12);
        text-align: center;
      }}
      h1 {{
        margin: 0 0 1rem;
        font-size: clamp(2rem, 6vw, 4rem);
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }}
      p {{
        margin: 0;
        font-size: 1.1rem;
      }}
      .accent {{
        color: var(--accent);
      }}
    </style>
  </head>
  <body>
    <main>
      <p class="accent">AWS Static Website Hosting</p>
      <h1>{full_name}</h1>
      <p>Hosted on Amazon S3</p>
    </main>
  </body>
</html>
"""


def write_simple_site(first_name: str, last_name: str, output_dir: str) -> Path:
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    index_path = target_dir / "index.html"
    index_path.write_text(
        generate_index_html(first_name, last_name),
        encoding="utf-8",
    )
    return index_path


def configure_bucket_for_website(aws_s3_client, bucket_name: str, index_document: str):
    aws_s3_client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        },
    )
    aws_s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=PUBLIC_READ_POLICY % bucket_name,
    )
    aws_s3_client.put_bucket_website(
        Bucket=bucket_name,
        WebsiteConfiguration={
            "IndexDocument": {"Suffix": index_document},
        },
    )


def upload_directory(aws_s3_client, bucket_name: str, site_dir: str):
    root = Path(site_dir).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Directory was not found: {root}")

    uploaded_files = []
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue

        object_key = file_path.relative_to(root).as_posix()
        content_type, _ = mimetypes.guess_type(str(file_path))
        extra_args = {"ContentType": content_type} if content_type else None

        if extra_args:
            aws_s3_client.upload_file(
                str(file_path),
                bucket_name,
                object_key,
                ExtraArgs=extra_args,
            )
        else:
            aws_s3_client.upload_file(str(file_path), bucket_name, object_key)

        uploaded_files.append(object_key)

    return uploaded_files


def website_url(bucket_name: str) -> str:
    region_name = getenv("aws_region_name", "us-east-1")
    return f"http://{bucket_name}.s3-website-{region_name}.amazonaws.com"


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "generate":
        index_path = write_simple_site(args.first_name, args.last_name, args.output_dir)
        print(f"Generated static page: {index_path}")
        return

    s3_client = init_s3_client()

    match args.command:
        case "host":
            configure_bucket_for_website(
                s3_client,
                args.bucket_name,
                args.index_document,
            )
            uploaded_files = upload_directory(s3_client, args.bucket_name, args.site_dir)
            print(f"Uploaded files: {len(uploaded_files)}")
            for object_key in uploaded_files:
                print(object_key)
            print(f"Website URL: {website_url(args.bucket_name)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    try:
        main()
    except ClientError as error:
        logging.error(
            "%s: %s",
            error.response["Error"].get("Code"),
            error.response["Error"].get("Message"),
        )
    except FileNotFoundError as error:
        logging.error(error)
