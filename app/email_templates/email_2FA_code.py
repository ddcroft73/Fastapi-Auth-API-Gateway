
style = '''
    /* CSS styles will be here */
        body {
    font-family: Arial, sans-serif;
    color: #333;
    background-color: rgb(162, 152, 152);
    margin: 0;
    padding: 0;
}

.email-container {
    max-width: 600px;
    margin: auto;
    margin-top: 20px;
    background-color: #d8d5d5;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
    border-radius: 8px;
}

header img {
    display: block;
    margin: 0 auto;
}

main {
    text-align: center;
}

.auth-code {
    font-size: 24px;
    font-family: 'Courier New', monospace;
    background-color: #eef;
    margin: 20px 0;
    padding: 10px;
    display: inline-block;
    border: 1px solid black;
    border-radius: 5px;
}

.info {
    font-size: 14px;
    color: #666;
}

footer p {
    font-size: 12px;
    text-align: center;
    color: #777;
}

'''



# Buold an email template that will be used to sent the 2FA code to the user.
def build_template_2FA_code(code_2FA: str, email: str) -> str: 
    template_2FA = f'''
    <!DOCTYPE html>
<html>
<head>
    <title>Two-Factor Authentication</title>
    <style>
    {style}
    </style>
</head>
<body>
    <div class="email-container">
        <header>
            <img src="path_to_life_package_logo.png" alt="Life Package Logo">
        </header>
        <main>
            <h1>Two-Factor Authentication</h1>
            <p>Enter the code below to complete your sign-in.</p>
            <div class="auth-code">{code_2FA}</div>
            <p class="info">This code is valid for 10 minutes. Never share this code with anyone.</p>
        </main>
        <footer>
            <p>Need help? <a href="support_link">Contact Support</a></p>
        </footer>
    </div>
</body>
</html>
    '''
    return template_2FA

