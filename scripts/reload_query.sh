set -x

NEW_QUERY=$1
QUERY_RESULTS_FILE=$2

python3 script.py search --query "$NEW_QUERY" > $QUERY_RESULTS_FILE
python3 scripts/track_names.py < $QUERY_RESULTS_FILE
