

def build_pword_reset_template(
    link: str, proj_name: str, email: str
) -> str:
    email_HTML_code: str = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset {proj_name}</title>
</head>
<body style="margin-top: 20px; padding: 0; font-family:  'Segoe UI', 'Roboto', 'Oxygen','Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',    sans-serif;">
    <table role="presentation" width="100%" style="max-width: 600px; margin: auto; background-color: #F9F9F9;">
        <tr>
            <td style="background-color: #333;  color: #FFF; text-align: center; padding: 20px;  border-radius: 8px;">
                <!--<img src="path-to-your-logo.png" alt="Your Logo" width="100" style="vertical-align: middle;">-->
                <h1>Life Package<span style="font-size: 16px; position: relative; top: -12px;"> &#8482;</span></h1>
                <h1 style="margin: 0; font-size: 24px; ">Reset your password</h1>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px; text-align: left;">
                <p style="color: #333; margin: 20px 0;">
                    Hello {email},
                    <br>
                    We have sent you this email in response to your request to reset your password for {proj_name}. Click the button
                    below and you will be taken to a form where you can create a new password.
                </p>
                <br>
                <a href="{link}" target="_blank" style="background-color: #0056b3; color: #FFF; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block;">Reset Password</a>
                <p style="color: #666; margin: 20px 0;">
                    Please ignore this email if you did not request a password change... and start asking some questions, cause somebody DID.
                </p>
            </td>
        </tr>
        <tr>
            <td style="background-color: #333; color: #FFF; padding: 15px; text-align: left;  border-radius: 8px;">
                <p style="font-size: 12px; margin: 0;">
                    <a href="mailto:support@lifepakage.app">support@lifepakage.app</a>

                    
                </p>
                <p style="font-size: 12px; margin: 10px 0 0 0;">
                    {proj_name} © All Rights Reserved
                </p>
                <!--
                <div style="margin-top: 10px;">
                    <a href="your-facebook-url" target="_blank">FB</a> |
                    <a href="your-twitter-url" target="_blank">TW</a> |
                    <a href="your-linkedin-url" target="_blank">IN</a>
                </div>-->
            </td>
        </tr>
    </table>
</body>
</html>
    """

    return email_HTML_code