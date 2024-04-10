set -x

NEW_QUERY=$1
QUERY_RESULTS_FILE=$2

SCRIPT_DIR=$(dirname $0)
ROOT_DIR=$(dirname $SCRIPT_DIR)

python3 $ROOT_DIR/script.py search-song --query "$NEW_QUERY" > $QUERY_RESULTS_FILE
python3 $SCRIPT_DIR/track_names.py < $QUERY_RESULTS_FILE
