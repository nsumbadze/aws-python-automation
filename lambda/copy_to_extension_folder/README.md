# Lambda - Copy To Extension Folder

AWS Lambda function triggered by S3 object creation.

When a file is uploaded to a bucket, the function copies that object into a folder that matches the file extension.

Examples:

- `image.png` -> `png/image.png`
- `report.pdf` -> `pdf/report.pdf`
- `archive.zip` -> `zip/archive.zip`
- `file_without_extension` -> `unknown/file_without_extension`

## File

- `lambda_function.py`

## AWS Lambda setup

1. Open AWS Lambda in the AWS Console.
2. Create a new function.
3. Choose `Author from scratch`.
4. Runtime: `Python 3.x`
5. Execution role: `Use an existing role`
6. Select `LabRole`
7. Create the function.
8. Replace the default code with the contents of `lambda_function.py`.
9. Deploy the function.

## S3 trigger setup

1. Open the Lambda function.
2. Add trigger.
3. Choose `S3`.
4. Select your bucket.
5. Event type: `PUT` / object created.
6. Save the trigger.

## Notes

- The function copies the file; it does not delete the original object.
- It skips objects that are already inside the target extension folder to avoid recursive copying.
- If you upload `hello.txt`, the copied object will be `txt/hello.txt`.
