style = '''
 <style>
    body {
      margin: 0;
      padding: 0;
      font-family: Arial, sans-serif;
      background-color: #f7f7f7;
    }
    .container {
      width: 100%;
      max-width: 600px;
      margin: 0 auto;
      text-align: center;
      padding: 20px;
    }
    .title {
      font-size: 24px;
      font-weight: bold;
      margin-top: 40px;
    }
    .text {
      margin-top: 20px;
    }
    .button {
      display: inline-block;
      margin-top: 40px;
      background-color: #007bff;
      color: #fff;
      text-decoration: none;
      font-size: 18px;
      font-weight: bold;
      padding: 10px 20px;
      border-radius: 5px;
    }
  </style>
'''


def build_template_verify(link: str) -> str:
    verify_email_page: str = f'''
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Email Template</title>
 {style}
</head>
<body>
  <div class="container">
    <div class="title">Email Template</div>
    <div class="text">This is the beginning of my verify email template.</div>
    <a class="button" href="{link}" style="width: 100px; height: 100px;">Verify Email</a>
  </div>
</body>
</html>

'''
    return verify_email_page

def build_template_reset(link: str) -> str:
    pass