#!/bin/bash
# run_dashboard.sh - Launch the Cameroon Population Dashboard with data validation

set -e  # Exit on error

echo "========================================"
echo "Cameroon Population Dashboard"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in the correct directory
if [ ! -d "src" ] || [ ! -d "data" ]; then
    print_error "Please run this script from the project root directory!"
    echo "Current directory: $(pwd)"
    echo "Expected: cameroon-administrative-data-platform/"
    exit 1
fi

print_status "Project root directory verified"

# Check Python environment
print_status "Checking Python environment..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_success "Python found: $PYTHON_VERSION"

# Check if required packages are installed
print_status "Checking required packages..."

REQUIRED_PACKAGES=("pandas" "numpy" "geopandas" "plotly" "streamlit" "folium")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    print_warning "Missing packages: ${MISSING_PACKAGES[*]}"
    print_status "Installing missing packages..."
    pip install -r requirements.txt
    print_success "Packages installed"
else
    print_success "All required packages are installed"
fi

# Check for required data files
print_status "Checking for required data files..."

# Define required files
REQUIRED_FILES=(
    "data/output/cameroon_complete_dataset.csv"
    "data/output/cameroon_hierarchy.json"
    "data/output/summary.json"
    "data/external/geoBoundaries-CMR-ADM1.geojson"
    "data/external/geoBoundaries-CMR-ADM2.geojson"
    "data/external/geoBoundaries-CMR-ADM3.geojson"
)

# Optional but recommended files
OPTIONAL_FILES=(
    "data/external/whosonfirst-data-admin-cm-latest/whosonfirst-data-admin-cm-locality-point.shp"
    "data/output/population_2005.csv"
    "data/output/population_2010.csv"
    "data/output/population_2015.csv"
    "data/output/population_2020.csv"
    "data/output/population_2025.csv"
)

MISSING_FILES=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    print_error "Missing required data files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    print_status "Generating dataset..."

    # Run the dataset generation script
    if [ -f "src/scripts/generate_dataset.py" ]; then
        print_status "Running generate_dataset.py..."
        python3 -m src.scripts.generate_dataset

        if [ $? -eq 0 ]; then
            print_success "Dataset generated successfully!"
        else
            print_error "Failed to generate dataset"
            exit 1
        fi
    else
        print_error "generate_dataset.py not found!"
        exit 1
    fi
else
    print_success "All required data files found"
fi

# Check optional files and show warnings
print_status "Checking optional data files..."
for file in "${OPTIONAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_warning "Optional file not found: $file"
        print_warning "  Some dashboard features may be limited"
    fi
done

# Validate data quality
print_status "Validating data quality..."

# Check if CSV has data
CSV_LINES=$(wc -l < "data/output/cameroon_complete_dataset.csv")
if [ "$CSV_LINES" -lt 100 ]; then
    print_error "Dataset appears to be too small (only $CSV_LINES rows)"
    exit 1
else
    print_success "Dataset has $CSV_LINES rows"
fi

# Check for population data in JSON
if python3 -c "import json; f=open('data/output/cameroon_hierarchy.json'); d=json.load(f); assert 'hierarchy' in d" 2>/dev/null; then
    print_success "Hierarchy JSON is valid"
else
    print_error "Hierarchy JSON is invalid or missing required structure"
    exit 1
fi

# Check for geoBoundaries files
print_status "Checking geospatial data..."

if [ -f "data/external/geoBoundaries-CMR-ADM1.geojson" ]; then
    print_success "Region boundaries found"
else
    print_warning "Region boundaries not found - map features will be limited"
fi

# Display dataset statistics
print_status "Dataset Statistics:"

if [ -f "data/output/summary.json" ]; then
    python3 << EOF
import json
with open('data/output/summary.json', 'r') as f:
    data = json.load(f)
print(f"  - Total Villages: {data.get('total_villages', 'N/A'):,}")
print(f"  - Total Regions: {data.get('total_regions', 'N/A')}")
print(f"  - Unique Postal Codes: {data.get('unique_postal_codes', 'N/A'):,}")
if 'population_by_year' in data:
    print(f"  - Population 2005: {data['population_by_year'].get('2005', 0):,.0f}")
    print(f"  - Population 2025: {data['population_by_year'].get('2025', 0):,.0f}")
EOF
else
    print_warning "summary.json not found - cannot display statistics"
fi

# Check for Streamlit
print_status "Checking Streamlit installation..."

if ! command -v streamlit &> /dev/null; then
    print_warning "Streamlit command not found, installing..."
    pip install streamlit
fi

print_success "Streamlit is available"

# Check available port
PORT=8501
print_status "Checking port $PORT..."

if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port $PORT is already in use"
    PORT=$((PORT + 1))
    print_status "Using alternative port: $PORT"
fi

# Create a temporary file to store dashboard PID
DASHBOARD_PID_FILE="/tmp/cameroon_dashboard.pid"

# Kill existing dashboard if running
if [ -f "$DASHBOARD_PID_FILE" ]; then
    OLD_PID=$(cat "$DASHBOARD_PID_FILE")
    if kill -0 $OLD_PID 2>/dev/null; then
        print_status "Stopping existing dashboard (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
    rm "$DASHBOARD_PID_FILE"
fi

# Create logs directory
mkdir -p logs

# Launch the dashboard
echo ""
echo "========================================"
print_success "Starting Dashboard..."
echo "========================================"
echo ""
echo "Dashboard URL: http://localhost:$PORT"
echo "Log file: logs/dashboard.log"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Run dashboard with logging
streamlit run src/visualization/dashboard.py \
    --server.port $PORT \
    --server.address localhost \
    --server.headless true \
    --browser.serverAddress localhost \
    --browser.serverPort $PORT \
    --logger.level info \
    2>&1 | tee logs/dashboard.log &

# Save PID
DASHBOARD_PID=$!
echo $DASHBOARD_PID > "$DASHBOARD_PID_FILE"

# Wait a moment for the server to start
sleep 3

# Check if dashboard started successfully
if kill -0 $DASHBOARD_PID 2>/dev/null; then
    print_success "Dashboard started successfully (PID: $DASHBOARD_PID)"

    # Open browser on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "Opening browser..."
        open "http://localhost:$PORT"
    # Open browser on Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Opening browser..."
        xdg-open "http://localhost:$PORT" 2>/dev/null || echo "Please open http://localhost:$PORT in your browser"
    fi

    echo ""
    echo "========================================"
    print_success "Dashboard is running!"
    echo "========================================"
    echo ""
    echo "To stop the dashboard, run:"
    echo "  kill $DASHBOARD_PID"
    echo "  or"
    echo "  pkill -f 'streamlit run'"
    echo ""

    # Wait for the dashboard process
    wait $DASHBOARD_PID
else
    print_error "Failed to start dashboard"
    exit 1
fi