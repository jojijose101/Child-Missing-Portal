import pymysql

pymysql.install_as_MySQLdb()

# Monkey patch for mysqlclient version compatibility
try:
    import MySQLdb
    if not hasattr(MySQLdb, 'version_info') or MySQLdb.version_info < (2, 2, 1):
        MySQLdb.version_info = (2, 2, 1, "final", 0)
        MySQLdb.version = "2.2.1"
except ImportError:
    pass