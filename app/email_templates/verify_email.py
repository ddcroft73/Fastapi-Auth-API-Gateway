style = '''
 <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: Arial, sans-serif;
            background-color: #e2dfdf;
            display: flex;
            flex-direction: column;
            justify-content: center; /* This helps to center the container vertically */
            align-items: center; /* This ensures the container is horizontally centered */
            min-height: 100vh;
        }

        .container {
            margin-top: 40px;
            width: 100%;
            max-width: 600px;
            text-align: center;
            padding: 40px 20px;
            background-color: #fff;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }


        .logo-placeholder {
            width: 60px;
            height: 60px;
            background-color: #ddd;
            margin: 0 auto;
            border-radius: 8px;
        }

        .text {
            margin-top: 30px;
            margin-bottom: 10px;
            font-size: 26px;
            font-weight: bold;
        }

        .info-text {
            margin-bottom: 30px;
            font-size: 16px;
            color: #555;
            line-height: 1.4;
            padding: 0 10px;
            /* Add a little padding to prevent text from sticking to the edges */
        }

        .button {
            display: block;
            width: calc(100% - 40px);  /* Adjusting the width directly */
            background-color: #007bff;
            color: #fff;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
            padding: 10px 0;
            border-radius: 5px;
            transition: background-color 0.3s;
            margin: 0 auto;
        }

        .button:hover {
            background-color: #0056b3;
        }

        footer {
            margin-top: auto;
            text-align: center;
            padding: 20px 0;
            font-size: 14px;
            color: #666;
        }

        /* Responsive styles */
        @media only screen and (max-width: 375px) {
            .container {
                padding: 60px 15px;
                /* Increased the side padding for better spacing */
            }

            .logo-placeholder {
                width: 50px;
                height: 50px;
            }

            .text {
                font-size: 24px;
            }

            .info-text {
                font-size: 14px;
                line-height: 1.3;
            }

            .button {
                font-size: 16px;
            }
        }
    </style>
'''


def build_template_verify(link: str, proj_name: str) -> str:
    verify_email_page: str = f'''
<!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <title>{proj_name} verify email.</title>
 {style}
</head>

<body>
    <div class="container">
        <div class="logo-placeholder"></div>
        <div class="text">Verify Your Email Address</div>
        <div class="info-text">
            Please confirm that this is your correct email address, as it will serve as your primary identification within Life
            Package. Once verified, if you wish to modify your email later, you can easily do so from your user settings.
        </div>
        <a class="button" href="{link}">Verify Email</a>
    </div>
    <footer>
        © 2023 Life Package. All rights reserved. <a href="#">Privacy Policy</a> | <a href="#">Terms of Service</a>
    </footer>
</body>

</html>

'''
    return verify_email_page

def build_template_reset(link: str, proj_name: str) -> str:
    pass