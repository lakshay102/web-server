from datetime import datetime

print("Content-Type: text/html\n")
print(f"""\
<html>
<body>
<p>Generated {datetime.now()}</p>
</body>
</html>
""")
