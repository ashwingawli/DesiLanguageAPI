# Oracle Autonomous Database Wallet Setup Guide

This guide shows how to configure the DesiLanguage application to use an Oracle Autonomous Database with wallet authentication.

## Wallet Configuration Overview

Your Oracle Autonomous Database wallet is located at:
```
~/projects/oracle_conn/desidb_wallet/
```

### Wallet Contents
The wallet contains the following files:
- **tnsnames.ora**: TNS connection definitions
- **sqlnet.ora**: SQL*Net configuration
- **cwallet.sso**: Auto-login wallet (SSO)
- **ewallet.p12**: Encrypted wallet
- **ojdbc.properties**: JDBC connection properties
- **keystore.jks**: Java keystore
- **truststore.jks**: Java truststore

## Available TNS Aliases

Your `tnsnames.ora` file contains these connection options:

| Alias | Purpose | Performance | Concurrency |
|-------|---------|-------------|-------------|
| `desidb_high` | High performance | Highest | Lower |
| `desidb_medium` | Balanced | Medium | Medium |
| `desidb_low` | High concurrency | Lower | Highest |
| `desidb_tp` | Transaction processing | Optimized for OLTP | Medium |
| `desidb_tpurgent` | Urgent transactions | Highest priority | Lower |

**Recommendation**: Use `desidb_high` for development and `desidb_medium` for production.

## Environment Configuration

### 1. Create Environment File

Copy the wallet configuration template:
```bash
cp .env.wallet.example .env
```

Or use the pre-configured DesiDB environment:
```bash
cp .env.desidb .env
```

### 2. Update Environment Variables

Edit `.env` file with your credentials:

```bash
# Database Connection using TNS Alias
DB_URL=oracle+cx_oracle://ADMIN:your_admin_password@desidb_high

# Google Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Oracle Wallet Configuration
WALLET_LOCATION=/home/ashwin/projects/oracle_conn/desidb_wallet
WALLET_PASSWORD=Adbwallet@2025
TNS_ALIAS=desidb_high

# Oracle Connection Pool Settings
ORACLE_POOL_SIZE=5
ORACLE_MAX_OVERFLOW=10
ORACLE_POOL_RECYCLE=3600
```

## Connection String Format

### Wallet-Based Connection
When using Oracle wallet authentication, use the TNS alias format:

```
oracle+cx_oracle://username:password@tns_alias
```

Examples:
```bash
# High performance connection
DB_URL=oracle+cx_oracle://ADMIN:mypassword@desidb_high

# Medium performance connection  
DB_URL=oracle+cx_oracle://ADMIN:mypassword@desidb_medium

# High concurrency connection
DB_URL=oracle+cx_oracle://ADMIN:mypassword@desidb_low
```

## Testing the Connection

### 1. Run Connection Test Script

```bash
python test_wallet_connection.py
```

This script will:
- Verify all wallet files are present
- Test connections to different TNS aliases
- Validate application configuration
- Display database information

### 2. Manual Testing

You can also test manually using Python:

```python
import os
import cx_Oracle

# Set wallet location
os.environ["TNS_ADMIN"] = "/home/ashwin/projects/oracle_conn/desidb_wallet"

# Connect using TNS alias
connection = cx_Oracle.connect("ADMIN", "your_password", "desidb_high")

# Test query
cursor = connection.cursor()
cursor.execute("SELECT 'Connected to ' || sys_context('USERENV', 'DB_NAME') FROM dual")
result = cursor.fetchone()
print(result[0])

cursor.close()
connection.close()
```

## Application Setup

### 1. Install Dependencies

```bash
pip install cx-Oracle oracledb
```

### 2. Set Environment Variables

The application will automatically set `TNS_ADMIN` when configured:

```python
# This happens automatically in app/utils/database.py
if settings.uses_wallet and settings.WALLET_LOCATION:
    os.environ["TNS_ADMIN"] = settings.WALLET_LOCATION
```

### 3. Run Database Migrations

```bash
# Create initial Oracle schema
alembic upgrade oracle_001
```

### 4. Start Application

```bash
python run.py
```

## Configuration Details

### Automatic Environment Setup

The application automatically configures Oracle environment variables:

```python
# app/utils/database.py
if settings.uses_wallet and settings.WALLET_LOCATION:
    os.environ["TNS_ADMIN"] = settings.WALLET_LOCATION
    if settings.ORACLE_HOME:
        os.environ["ORACLE_HOME"] = settings.ORACLE_HOME
```

### Wallet Password Handling

For encrypted wallets (like yours with password `Adbwallet@2025`), the application automatically passes the wallet password to the Oracle driver:

```python
# Automatic wallet password handling
if settings.uses_wallet:
    if settings.WALLET_PASSWORD:
        connect_args["wallet_password"] = settings.WALLET_PASSWORD
```

This ensures secure access to encrypted wallet files without manual intervention.

### Connection Pool Configuration

Oracle-specific connection pooling is configured for optimal performance:

```python
engine = create_engine(
    connection_string,
    pool_size=settings.ORACLE_POOL_SIZE,           # 5
    max_overflow=settings.ORACLE_MAX_OVERFLOW,     # 10
    pool_recycle=settings.ORACLE_POOL_RECYCLE,     # 3600 seconds
    pool_pre_ping=True,
    echo=False,
    connect_args={
        "encoding": "UTF-8",
        "nencoding": "UTF-8"
    }
)
```

## Security Considerations

### 1. Wallet Security
- Keep wallet files secure and limit access permissions
- Never commit wallet files to version control
- Use environment variables for sensitive configuration

### 2. Password Management
- Use strong passwords for database users
- Consider using environment-specific passwords
- Rotate passwords regularly

### 3. Connection Security
- Wallet provides SSL/TLS encryption automatically
- All connections use Oracle's secure protocol (TCPS)
- Certificate validation is enabled by default

## Troubleshooting

### Common Issues

#### 1. TNS-12154: Could not resolve connect identifier

**Problem**: TNS alias not found
**Solution**: 
- Verify `TNS_ADMIN` environment variable is set correctly
- Check that `tnsnames.ora` exists in wallet directory
- Ensure TNS alias name matches exactly (case sensitive)

```bash
echo $TNS_ADMIN
ls -la $TNS_ADMIN/tnsnames.ora
```

#### 2. ORA-28000: Account is locked

**Problem**: Database user account is locked
**Solution**: Unlock the account in Oracle Cloud Console or contact administrator

#### 3. Connection timeout

**Problem**: Network connectivity issues
**Solution**: 
- Check firewall settings
- Verify Oracle Cloud network access rules
- Test connection from Oracle SQL Developer first

#### 4. Wallet file permissions

**Problem**: Cannot read wallet files
**Solution**: 
```bash
chmod 600 ~/projects/oracle_conn/desidb_wallet/*
chmod 755 ~/projects/oracle_conn/desidb_wallet/
```

### Debug Connection

Enable connection debugging:

```python
# In app/utils/database.py, temporarily set echo=True
engine = create_engine(
    connection_string,
    echo=True,  # Enable SQL logging
    # ... other settings
)
```

### Verify Wallet Configuration

Check wallet configuration:

```bash
# Verify TNS_ADMIN is set
echo $TNS_ADMIN

# Check wallet files
ls -la ~/projects/oracle_conn/desidb_wallet/

# Verify tnsnames.ora content
cat ~/projects/oracle_conn/desidb_wallet/tnsnames.ora

# Test with SQL*Plus (if available)
sqlplus ADMIN@desidb_high
```

## Performance Tuning

### Connection Pool Sizing

Adjust pool settings based on your application load:

```bash
# For low traffic
ORACLE_POOL_SIZE=2
ORACLE_MAX_OVERFLOW=5

# For high traffic  
ORACLE_POOL_SIZE=10
ORACLE_MAX_OVERFLOW=20

# For development
ORACLE_POOL_SIZE=1
ORACLE_MAX_OVERFLOW=2
```

### TNS Alias Selection

Choose appropriate TNS alias based on workload:

- **Development**: `desidb_low` (cost-effective)
- **Testing**: `desidb_medium` (balanced)
- **Production**: `desidb_high` (best performance)
- **High-throughput**: `desidb_tp` (transaction optimized)

## Monitoring

### Connection Health

Monitor connection pool health:

```python
# Check active connections
print(f"Pool size: {engine.pool.size()}")
print(f"Checked in: {engine.pool.checkedin()}")
print(f"Checked out: {engine.pool.checkedout()}")
```

### Database Metrics

Use Oracle Cloud Console to monitor:
- CPU utilization
- Storage usage
- Connection count
- Query performance

## Wallet Expiry

Your wallet expires on: **2030-08-09 13:25:59 UTC**

### Before Expiry
1. Download new wallet from Oracle Cloud Console
2. Replace wallet files in `~/projects/oracle_conn/desidb_wallet/`
3. Restart application
4. Test connections

### Renewal Process
1. Login to Oracle Cloud Console
2. Navigate to Autonomous Database
3. Click "DB Connection" 
4. Download new wallet
5. Extract to wallet directory
6. Update environment if needed

## Summary

The Oracle wallet configuration provides secure, automatic SSL authentication to your Autonomous Database. The setup includes:

✅ **Wallet Integration**: Automatic TNS_ADMIN configuration  
✅ **Multiple Aliases**: High, medium, low performance options  
✅ **Connection Pooling**: Optimized for Oracle performance  
✅ **Security**: SSL/TLS encryption with certificate validation  
✅ **Testing Tools**: Connection verification scripts  
✅ **Documentation**: Complete setup and troubleshooting guide  

Your application is now ready to connect securely to Oracle Autonomous Database using wallet authentication!