PGPass="<%=cypher.read('secret/postgres')%>"
DB_IP="<%=evars.DB_IP%>"
DB_PORT="<%=evars.DB_PORT%>"

apt install -y postgresql-client
export PGPASSWORD="<%=cypher.read('secret/postgres')%>"
psql -h $DB_IP -p $DB_PORT -U admin -d template1 -c "CREATE DATABASE todo;"
psql -h $DB_IP -p $DB_PORT -U admin -d template1 -c "CREATE USER todouser WITH PASSWORD '$PGPass';"
psql -h $DB_IP -p $DB_PORT -U admin -d template1 -c "grant all privileges on database todo to todouser;"
psql -h $DB_IP -p $DB_PORT -U admin -d todo -c "CREATE TABLE todos (item text);"
psql -h $DB_IP -p $DB_PORT -U admin -d todo -c "grant all privileges on table todos to todouser;"

mkdir -p /opt/todo
cat << EOF > /opt/todo/config.env
# POSTGRES CONFIG
PG_HOST=$DB_IP

# OPTIONAL TO OVERRIDE DEFAULTS
PG_PORT=$DB_PORT               # default is 5432
PG_USER=todouser               # default is postgres
PG_PASSWORD=Password123?       # default is Password123?
PG_DATABASE=todo               # default is todos
#APP_SERVER_PORT=              # default is 8090
EOF