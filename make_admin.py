import sqlite3

# Database se connect karein
conn = sqlite3.connect("dasai_professional.db")
c = conn.cursor()

# Aapke email ko Admin set karne ki query
c.execute("UPDATE users SET is_admin = 1 WHERE email = 'shankarjitdas2@gmail.com'")
conn.commit()
conn.close()

print("Success! shankarjitdas2@gmail.com ab Admin ban chuka hai.")

