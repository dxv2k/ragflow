#!/bin/bash

# RAGFlow Complete Backup Script
# This script creates backups of all RAGFlow components: MySQL, MinIO, and Elasticsearch

set -e

# Configuration
BACKUP_DIR="ragflow-backup-$(date +%Y%m%d-%H%M%S)"
MYSQL_CONTAINER="ragflow-mysql"
MINIO_CONTAINER="ragflow-minio"
ES_CONTAINER="ragflow-es-01"

# Database credentials (from .env and service_conf.yaml)
MYSQL_USER="root"
MYSQL_PASSWORD="infini_rag_flow"
MYSQL_DB="rag_flow"
MYSQL_HOST="127.0.0.1"
MYSQL_PORT="5455"

# MinIO credentials
MINIO_USER="rag_flow"
MINIO_PASSWORD="infini_rag_flow"
MINIO_HOST="127.0.0.1"
MINIO_PORT="9000"

# Elasticsearch credentials
ES_USER="elastic"
ES_PASSWORD="infini_rag_flow"
ES_HOST="127.0.0.1"
ES_PORT="1200"

echo "Starting RAGFlow backup process..."
echo "Backup directory: $BACKUP_DIR"

# Create backup directory
mkdir -p "$BACKUP_DIR"
cd "$BACKUP_DIR"

# Function to check if container is running
check_container() {
    if docker ps --format "table {{.Names}}" | grep -q "^$1$"; then
        echo "✓ Container $1 is running"
        return 0
    else
        echo "✗ Container $1 is not running"
        return 1
    fi
}

# Function to backup MySQL
backup_mysql() {
    echo "Starting MySQL backup..."
    
    if ! check_container "$MYSQL_CONTAINER"; then
        echo "MySQL container is not running. Skipping MySQL backup."
        return 1
    fi
    
    echo "Exporting MySQL database..."
    docker exec "$MYSQL_CONTAINER" mysqldump \
        -h "$MYSQL_HOST" \
        -P "$MYSQL_PORT" \
        -u"$MYSQL_USER" \
        -p"$MYSQL_PASSWORD" \
        "$MYSQL_DB" > ragflow-mysql.sql
    
    if [ $? -eq 0 ]; then
        echo "✓ MySQL backup completed successfully"
        ls -lh ragflow-mysql.sql
    else
        echo "✗ MySQL backup failed"
        return 1
    fi
}

# Function to backup MinIO
backup_minio() {
    echo "Starting MinIO backup..."
    
    if ! check_container "$MINIO_CONTAINER"; then
        echo "MinIO container is not running. Skipping MinIO backup."
        return 1
    fi
    
    # Create MinIO alias
    echo "Setting up MinIO alias..."
    docker exec "$MINIO_CONTAINER" mc alias set local \
        "http://$MINIO_HOST:$MINIO_PORT" \
        "$MINIO_USER" \
        "$MINIO_PASSWORD"
    
    # Create export directory
    mkdir -p ragflow-minio-export
    
    # Copy all data from MinIO
    echo "Copying MinIO data..."
    docker exec "$MINIO_CONTAINER" mc cp --recursive local/ ragflow-minio-export/
    
    if [ $? -eq 0 ]; then
        echo "✓ MinIO backup completed successfully"
        # Create compressed archive
        tar -czf ragflow-minio-backup.tar.gz ragflow-minio-export/
        echo "MinIO backup size: $(du -h ragflow-minio-backup.tar.gz | cut -f1)"
        rm -rf ragflow-minio-export  # Clean up uncompressed data
    else
        echo "✗ MinIO backup failed"
        return 1
    fi
}

# Function to backup Elasticsearch (optional for newer versions)
backup_elasticsearch() {
    echo "Starting Elasticsearch backup..."
    
    if ! check_container "$ES_CONTAINER"; then
        echo "Elasticsearch container is not running. Skipping Elasticsearch backup."
        return 1
    fi
    
    # Set Elasticsearch URL
    ES_URL="http://$ES_USER:$ES_PASSWORD@$ES_HOST:$ES_PORT"
    
    # Check if Elasticsearch is accessible
    if ! curl -s "$ES_URL/_cluster/health" > /dev/null; then
        echo "Elasticsearch is not accessible. Skipping Elasticsearch backup."
        return 1
    fi
    
    echo "Checking Elasticsearch indices..."
    INDICES=$(curl -s "$ES_URL/_cat/indices/ragflow_*?h=index" | grep -v "^$")
    
    if [ -z "$INDICES" ]; then
        echo "No ragflow indices found. Elasticsearch backup may not be needed for newer versions."
        return 0
    fi
    
    echo "Found ragflow indices:"
    echo "$INDICES"
    
    # Create directory for Elasticsearch dumps
    mkdir -p es_dumps && cd es_dumps
    
    # Export each index using elasticdump
    for index in $INDICES; do
        echo "Exporting index: $index"
        
        # Export mappings
        docker run --rm -v "$PWD":/data elasticdump/elasticsearch-dump \
            --input="$ES_URL/$index" \
            --output=/data/${index}_mapping.json \
            --type=mapping
        
        # Export settings
        docker run --rm -v "$PWD":/data elasticdump/elasticsearch-dump \
            --input="$ES_URL/$index" \
            --output=/data/${index}_settings.json \
            --type=settings
        
        # Export data
        docker run --rm -v "$PWD":/data elasticdump/elasticsearch-dump \
            --input="$ES_URL/$index" \
            --output=/data/${index}.json \
            --type=data
    done
    
    cd ..
    
    if [ $? -eq 0 ]; then
        echo "✓ Elasticsearch backup completed successfully"
        # Create compressed archive
        tar -czf ragflow-elasticsearch-backup.tar.gz es_dumps/
        echo "Elasticsearch backup size: $(du -h ragflow-elasticsearch-backup.tar.gz | cut -f1)"
        rm -rf es_dumps  # Clean up uncompressed data
    else
        echo "✗ Elasticsearch backup failed"
        return 1
    fi
}

# Function to create backup summary
create_summary() {
    echo "Creating backup summary..."
    
    cat > backup-summary.txt << EOF
RAGFlow Backup Summary
======================
Backup Date: $(date)
Backup Directory: $BACKUP_DIR

Components Backed Up:
EOF
    
    if [ -f "ragflow-mysql.sql" ]; then
        echo "- MySQL: $(du -h ragflow-mysql.sql | cut -f1)" >> backup-summary.txt
    fi
    
    if [ -f "ragflow-minio-backup.tar.gz" ]; then
        echo "- MinIO: $(du -h ragflow-minio-backup.tar.gz | cut -f1)" >> backup-summary.txt
    fi
    
    if [ -f "ragflow-elasticsearch-backup.tar.gz" ]; then
        echo "- Elasticsearch: $(du -h ragflow-elasticsearch-backup.tar.gz | cut -f1)" >> backup-summary.txt
    fi
    
    cat >> backup-summary.txt << EOF

Total Backup Size: $(du -sh . | cut -f1)

Restore Instructions:
1. Copy this backup directory to the target server
2. Follow the migration guide to restore each component
3. Start with MySQL, then MinIO, and finally Elasticsearch if needed

Note: For newer RAGFlow versions, Elasticsearch data may be automatically
reconstructed when documents are accessed. Consider testing without importing
Elasticsearch data first.
EOF
    
    echo "Backup summary created:"
    cat backup-summary.txt
}

# Main execution
echo "Checking container status..."
check_container "$MYSQL_CONTAINER"
check_container "$MINIO_CONTAINER"
check_container "$ES_CONTAINER"

echo ""
echo "Starting backup process..."

# Backup each component
backup_mysql
echo ""

backup_minio
echo ""

# Elasticsearch backup is optional for newer versions
read -p "Do you want to backup Elasticsearch data? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    backup_elasticsearch
    echo ""
fi

# Create backup summary
create_summary

echo ""
echo "Backup process completed!"
echo "Backup location: $(pwd)"
echo "Total backup size: $(du -sh . | cut -f1)"

# Create a single compressed archive of everything
cd ..
echo "Creating final compressed archive..."
tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"
echo "Final archive: ${BACKUP_DIR}.tar.gz ($(du -h "${BACKUP_DIR}.tar.gz" | cut -f1))"

echo ""
echo "Backup completed successfully!"
echo "Files created:"
echo "- ${BACKUP_DIR}/ (uncompressed backups)"
echo "- ${BACKUP_DIR}.tar.gz (compressed archive)"