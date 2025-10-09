#!/bin/bash

# RAGFlow Data Restoration Script
# This script automates the complete restoration process from an export archive

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESTORE_DIR="ragflow-restore"
EXPORT_ARCHIVE="ragflow-export-20251009-093724.tar.gz"
EXPORT_SCRIPT="ragflow-export.sh"

# Port configuration (to avoid conflicts with production)
ES_PORT=1201
MYSQL_PORT=5456
MINIO_CONSOLE_PORT=9004
MINIO_PORT=9005
REDIS_PORT=6383
SVR_HTTP_PORT=19382
FRONTEND_PORT=18081

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for container to be healthy
wait_for_container() {
    local container_name=$1
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $container_name to be healthy..."
    while [ $attempt -le $max_attempts ]; do
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep "$container_name" | grep -q "healthy"; then
            print_success "$container_name is healthy"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$container_name did not become healthy within expected time"
    return 1
}

# Main restoration function
main() {
    print_status "Starting RAGFlow restoration process..."
    
    # Check prerequisites
    check_prerequisites
    
    # Create restore environment
    create_restore_environment
    
    # Extract export archive
    extract_archive
    
    # Start containers
    start_containers
    
    # Restore MySQL
    restore_mysql
    
    # Restore MinIO
    restore_minio
    
    # Restore Elasticsearch
    restore_elasticsearch
    
    # Verify restoration
    verify_restoration
    
    print_success "RAGFlow restoration completed successfully!"
    print_status "Access your restored instance at: http://localhost:$FRONTEND_PORT"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if export archive exists
    if [ ! -f "$EXPORT_ARCHIVE" ]; then
        print_error "Export archive $EXPORT_ARCHIVE not found in current directory."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create restore environment
create_restore_environment() {
    print_status "Creating restore environment..."
    
    # Create restore directory
    if [ -d "$RESTORE_DIR" ]; then
        print_warning "Restore directory $RESTORE_DIR already exists. Backing up..."
        mv "$RESTORE_DIR" "${RESTORE_DIR}.backup.$(date +%Y%m%d%H%M%S)"
    fi
    
    mkdir -p "$RESTORE_DIR"
    cd "$RESTORE_DIR"
    
    # Copy configuration files
    print_status "Copying configuration files..."
    cp ../docker-compose-base.yml .
    cp ../docker-compose.yml .
    cp ../.env .env
    
    # Modify .env file for restore instance
    print_status "Modifying configuration for restore instance..."
    sed -i "s/ES_PORT=1200/ES_PORT=$ES_PORT/" .env
    sed -i "s/MYSQL_PORT=5455/MYSQL_PORT=$MYSQL_PORT/" .env
    sed -i "s/MINIO_CONSOLE_PORT=9001/MINIO_CONSOLE_PORT=$MINIO_CONSOLE_PORT/" .env
    sed -i "s/MINIO_PORT=9002/MINIO_PORT=$MINIO_PORT/" .env
    sed -i "s/REDIS_PORT=6382/REDIS_PORT=$REDIS_PORT/" .env
    sed -i "s/SVR_HTTP_PORT=9380/SVR_HTTP_PORT=$SVR_HTTP_PORT/" .env
    
    # Modify docker-compose.yml
    sed -i "s/container_name: ragflow-server/container_name: ragflow-restore-server/" docker-compose.yml
    sed -i "s/18081:81/$FRONTEND_PORT:81/" docker-compose.yml
    sed -i "s/9380:9380/$SVR_HTTP_PORT:9380/" docker-compose.yml
    
    # Modify docker-compose-base.yml
    sed -i "s/container_name: ragflow-mysql/container_name: ragflow-restore-mysql/" docker-compose-base.yml
    sed -i "s/container_name: ragflow-minio/container_name: ragflow-restore-minio/" docker-compose-base.yml
    sed -i "s/container_name: ragflow-redis/container_name: ragflow-restore-redis/" docker-compose-base.yml
    sed -i "s/container_name: ragflow-es-01/container_name: ragflow-restore-es-01/" docker-compose-base.yml
    
    # Create Elasticsearch transformation script
    print_status "Creating Elasticsearch transformation script..."
    cat > transform_es_bulk.py << 'EOF'
#!/usr/bin/env python3
import json
import os
import sys

def transform_es_bulk_file(input_file, output_file):
    """Transform Elasticsearch export file to bulk API format"""
    with open(input_file, 'r') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    
    with open(output_file, 'w') as f:
        for line in lines:
            if not line.strip():
                continue
                
            try:
                doc = json.loads(line)
                
                if '_index' in doc and '_source' in doc:
                    index_name = doc['_index']
                    doc_id = doc.get('_id')
                    source_data = doc['_source']
                    
                    if doc_id:
                        index_cmd = {"index": {"_index": index_name, "_id": doc_id}}
                    else:
                        index_cmd = {"index": {"_index": index_name}}
                    
                    f.write(json.dumps(index_cmd) + '\n')
                    f.write(json.dumps(source_data) + '\n')
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing line in {input_file}: {e}")
                continue
    
    print(f"Transformed {input_file} to {output_file}")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python transform_es_bulk.py <file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist")
        sys.exit(1)
    
    if input_file.endswith('_mapping.json') or input_file.endswith('_settings.json'):
        print(f"Skipping {input_file}")
        return
    
    output_file = input_file.replace('.json', '_bulk.json')
    transform_es_bulk_file(input_file, output_file)

if __name__ == '__main__':
    main()
EOF
    
    chmod +x transform_es_bulk.py
    
    print_success "Restore environment created"
}

# Extract export archive
extract_archive() {
    print_status "Extracting export archive..."
    tar -xzf "../$EXPORT_ARCHIVE"
    print_success "Archive extracted"
}

# Start containers
start_containers() {
    print_status "Starting RAGFlow containers..."
    docker compose -f docker-compose.yml -f docker-compose-base.yml up -d
    
    print_status "Waiting for containers to be healthy..."
    wait_for_container "ragflow-restore-mysql"
    wait_for_container "ragflow-restore-es-01"
    
    # Give extra time for all services to fully start
    sleep 10
    
    print_success "All containers are running"
}

# Restore MySQL database
restore_mysql() {
    print_status "Restoring MySQL database..."
    
    if [ ! -f "ragflow_mysql.sql" ]; then
        print_error "MySQL dump file not found in extracted archive"
        exit 1
    fi
    
    docker exec -i ragflow-restore-mysql mysql -uroot -pinfini_rag_flow ragflow < ragflow_mysql.sql
    
    print_success "MySQL database restored"
}

# Restore MinIO data
restore_minio() {
    print_status "Restoring MinIO data..."
    
    # Install MinIO client if not present
    if ! command_exists mc; then
        print_status "Installing MinIO client..."
        wget -q https://dl.min.io/client/mc/release/linux-amd64/mc
        chmod +x mc
        sudo mv mc /usr/local/bin/ 2>/dev/null || mv mc ~/bin/ 2>/dev/null || {
            export PATH=$PATH:$(pwd)
        }
    fi
    
    # Configure MinIO client
    mc alias set restore-minio http://localhost:$MINIO_PORT rag_flow infini_rag_flow
    
    # Create buckets
    print_status "Creating MinIO buckets..."
    mc mb restore-minio/ragflow 2>/dev/null || true
    mc mb restore-minio/ragflow-logs 2>/dev/null || true
    
    # Restore data if exists
    if [ -d "minio_data/ragflow" ]; then
        print_status "Copying ragflow bucket data..."
        mc cp --recursive minio_data/ragflow/ restore-minio/ragflow/
    fi
    
    if [ -d "minio_data/ragflow-logs" ]; then
        print_status "Copying ragflow-logs bucket data..."
        mc cp --recursive minio_data/ragflow-logs/ restore-minio/ragflow-logs/
    fi
    
    print_success "MinIO data restored"
}

# Restore Elasticsearch indices
restore_elasticsearch() {
    print_status "Restoring Elasticsearch indices..."
    
    # Get Elasticsearch container ID
    ES_CONTAINER=$(docker ps --format "{{.Names}}" | grep ragflow-restore-es-01)
    
    if [ -z "$ES_CONTAINER" ]; then
        print_error "Elasticsearch container not found"
        exit 1
    fi
    
    # Transform JSON files to bulk format
    print_status "Transforming Elasticsearch data files..."
    for file in *.json; do
        if ! echo "$file" | grep -q "_mapping.json$" && ! echo "$file" | grep -q "_settings.json$"; then
            python3 transform_es_bulk.py "$file"
        fi
    done
    
    # Import bulk files
    print_status "Importing Elasticsearch data..."
    for bulkfile in *_bulk.json; do
        print_status "Importing $bulkfile..."
        docker cp "$bulkfile" "$ES_CONTAINER:/tmp/"
        docker exec "$ES_CONTAINER" curl -X POST "http://localhost:9200/_bulk?pretty" \
            -H "Content-Type: application/x-ndjson" \
            -u "elastic:infini_rag_flow" \
            --data-binary @"/tmp/$bulkfile" > /dev/null
    done
    
    print_success "Elasticsearch indices restored"
}

# Verify restoration
verify_restoration() {
    print_status "Verifying restoration..."
    
    # Check if containers are running
    if ! docker ps | grep -q ragflow-restore-server; then
        print_error "RAGFlow server container is not running"
        exit 1
    fi
    
    # Check if frontend is accessible
    sleep 5
    if curl -s "http://localhost:$FRONTEND_PORT" | grep -q "RAGFlow"; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend might still be starting up..."
    fi
    
    # Display access information
    echo
    print_success "Restoration completed successfully!"
    echo
    echo "Access Information:"
    echo "=================="
    echo "RAGFlow Frontend: http://localhost:$FRONTEND_PORT"
    echo "RAGFlow API: http://localhost:$SVR_HTTP_PORT"
    echo "MinIO Console: http://localhost:$MINIO_CONSOLE_PORT"
    echo "  Username: rag_flow"
    echo "  Password: infini_rag_flow"
    echo
    echo "Container Status:"
    docker ps | grep ragflow-restore
    echo
}

# Run main function
main "$@"