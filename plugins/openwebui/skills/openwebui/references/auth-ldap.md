# LDAP Authentication

## Setting Up OpenLDAP with Docker

Docker Compose for OpenLDAP and phpLDAPadmin:

```yaml
version: "3.9"
services:
  ldap:
    image: osixia/openldap:1.5.0
    container_name: openldap
    environment:
      LDAP_ORGANISATION: "Example Inc"
      LDAP_DOMAIN: "example.org"
      LDAP_ADMIN_PASSWORD: admin
      LDAP_TLS: "false"
    volumes:
      - ./ldap/var:/var/lib/ldap
      - ./ldap/etc:/etc/ldap/slapd.d
    ports:
      - "389:389"
    networks: [ldapnet]

  phpldapadmin:
    image: osixia/phpldapadmin:0.9.0
    environment:
      PHPLDAPADMIN_LDAP_HOSTS: "ldap"
    ports:
      - "6443:443"
    networks: [ldapnet]

networks:
  ldapnet:
    driver: bridge
```

phpLDAPadmin is accessible at `https://localhost:6443`.

## Seeding a Sample User (LDIF)

```ldif
dn: ou=users,dc=example,dc=org
objectClass: organizationalUnit
ou: users

dn: uid=jdoe,ou=users,dc=example,dc=org
objectClass: inetOrgPerson
cn: John Doe
sn: Doe
uid: jdoe
mail: jdoe@example.org
userPassword: {PLAIN}password123
```

In production, always use hashed passwords. Generate with:

```bash
# Using slappasswd (inside the container)
docker exec openldap slappasswd -s your_password

# Using openssl
openssl passwd -6 your_password
```

Add the entry:

```bash
docker cp seed.ldif openldap:/seed.ldif
docker exec openldap ldapadd -x -D "cn=admin,dc=example,dc=org" -w admin -f /seed.ldif
```

## Verifying the LDAP Connection

```bash
ldapsearch -x -H ldap://localhost:389 \
  -D "cn=admin,dc=example,dc=org" -w admin \
  -b "dc=example,dc=org" "(uid=jdoe)"
```

## Configuring Open WebUI

Open WebUI reads these environment variables only on the first startup. Subsequent changes must be made in the Admin settings panel unless you have `ENABLE_PERSISTENT_CONFIG=false`.

```env
# Enable LDAP
ENABLE_LDAP="true"

# --- Server Settings ---
LDAP_SERVER_LABEL="OpenLDAP"
LDAP_SERVER_HOST="localhost"  # Or the IP/hostname of your LDAP server
LDAP_SERVER_PORT="389"        # Use 389 for plaintext/StartTLS, 636 for LDAPS
LDAP_USE_TLS="false"          # Set to "true" for LDAPS or StartTLS
LDAP_VALIDATE_CERT="false"    # Set to "true" in production with valid certs

# --- Bind Credentials ---
LDAP_APP_DN="cn=admin,dc=example,dc=org"
LDAP_APP_PASSWORD="admin"

# --- User Schema ---
LDAP_SEARCH_BASE="dc=example,dc=org"
LDAP_ATTRIBUTE_FOR_USERNAME="uid"
LDAP_ATTRIBUTE_FOR_MAIL="mail"
# LDAP_SEARCH_FILTER is optional and used for additional filtering conditions.
# The username filter is automatically added by Open WebUI, so do NOT include
# user placeholder syntax like %(user)s or %s - these are not supported.
# Leave empty for simple setups, or add group membership filters, e.g.:
# LDAP_SEARCH_FILTER="(memberOf=cn=allowed-users,ou=groups,dc=example,dc=org)"
```

### UI Configuration

1. Log in as an administrator.
2. Navigate to **Settings > General**.
3. Enable **LDAP Authentication**.
4. Fill in the fields corresponding to the environment variables above.
5. Save the settings and restart Open WebUI.

## Logging In

- **Login ID:** `jdoe`
- **Password:** `password123`

Upon successful login, a new user account with "User" role is created automatically.

## Troubleshooting

### `port must be an integer`

**Cause:** `LDAP_SERVER_PORT` is being passed as a string with quotes.
**Solution:** Remove quotes from the port value (`LDAP_SERVER_PORT=389`) and remove protocol prefixes from `LDAP_SERVER_HOST`.

### `[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred`

**Cause:** TLS handshake failure.
**Solution:**
- No TLS: Set `LDAP_USE_TLS="false"`, connect to port `389`
- LDAPS: Configure server for TLS on port `636`, set `LDAP_USE_TLS="true"`
- StartTLS: Connect on port `389`, set `LDAP_USE_TLS="true"`

### `err=49 text=` (Invalid Credentials)

**Cause:** Incorrect DN or password for bind attempt.
**Solution:**
1. Verify the password matches the `userPassword` in the LDIF
2. Check the User DN is correct (`uid=jdoe,ou=users,dc=example,dc=org`)
3. Test with `ldapwhoami`:
   ```bash
   ldapwhoami -x -H ldap://localhost:389 \
     -D "uid=jdoe,ou=users,dc=example,dc=org" -w "password123"
   ```
4. Reset password if needed using `ldapmodify` or `ldappasswd`

Example LDIF to change password:

```ldif
dn: uid=jdoe,ou=users,dc=example,dc=org
changetype: modify
replace: userPassword
userPassword: {PLAIN}newpassword
```

Apply with:

```bash
docker exec openldap ldapmodify -x -D "cn=admin,dc=example,dc=org" -w admin -f /path/to/change_password.ldif
```
