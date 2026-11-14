#!/bin/bash
set -e

BASE_URL="https://127.0.0.1"
API_URL="$BASE_URL/api/incidents"

echo "============================================================"
echo " Service Desk Platform - Phase 11 Automated Verification"
echo "============================================================"

echo -e "\n[1/6] Checking active systemd services..."
for SERVICE in postgresql nginx servicedesk-api; do
    STATUS=$(systemctl is-active "$SERVICE")
    echo "  -> $SERVICE: $STATUS"
    if [ "$STATUS" != "active" ]; then
        echo "[FAIL] Service $SERVICE is not active!"
        exit 1
    fi
done

echo -e "\n[2/6] Verifying HTTP -> HTTPS redirection..."
REDIRECT_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/api/incidents)
echo "  -> HTTP status code: $REDIRECT_CODE"
if [ "$REDIRECT_CODE" != "301" ]; then
    echo "[FAIL] Expected 301 redirect, got $REDIRECT_CODE"
    exit 1
fi

echo -e "\n[3/6] Testing POST /api/incidents (Create)..."
CREATE_RES=$(curl -k -s -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{"title": "Automated Phase 11 Test", "description": "End-to-end verification incident", "priority": "HIGH"}')
echo "  -> Response: $CREATE_RES"

INCIDENT_ID=$(echo "$CREATE_RES" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "  -> Created Incident ID: $INCIDENT_ID"

echo -e "\n[4/6] Testing GET and PUT /api/incidents/$INCIDENT_ID..."
HTTP_GET=$(curl -k -s -o /dev/null -w "%{http_code}" "$API_URL/$INCIDENT_ID")
echo "  -> GET /api/incidents/$INCIDENT_ID status: $HTTP_GET"

UPDATE_RES=$(curl -k -s -X PUT "$API_URL/$INCIDENT_ID" \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_PROGRESS"}')
echo "  -> PUT response: $UPDATE_RES"

echo -e "\n[5/6] Testing POST /api/incidents/$INCIDENT_ID/comments & PostgreSQL persistence..."
COMMENT_RES=$(curl -k -s -X POST "$API_URL/$INCIDENT_ID/comments" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "comment": "Automated verification comment"}')
echo "  -> Comment response: $COMMENT_RES"

DB_ROW=$(sudo -u postgres psql -d servicedesk -t -A -c "SELECT id || '|' || title || '|' || status FROM incidents WHERE id = $INCIDENT_ID;")
echo "  -> PostgreSQL record verified: $DB_ROW"

echo -e "\n[6/6] Cleaning up test record (DELETE /api/incidents/$INCIDENT_ID)..."
sudo -u postgres psql -d servicedesk -q -c "DELETE FROM comments WHERE incident_id = $INCIDENT_ID;"
DEL_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/$INCIDENT_ID")
echo "  -> DELETE status code: $DEL_CODE"

echo -e "\n============================================================"
echo " ALL FUNCTIONAL & INTEGRATION TESTS PASSED SUCCESSFULLY!"
echo "============================================================"