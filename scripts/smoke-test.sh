#!/usr/bin/env bash
# Test de fumée : construit et lance toute l'app dans Docker (projet et port à part, pour ne pas
# toucher à l'instance habituelle), puis vérifie les parcours essentiels de bout en bout.
#
#   ./scripts/smoke-test.sh
#
# Variables : SMOKE_PORT (8089 par défaut), SMOKE_PROJECT, SMOKE_BUILD=0 pour réutiliser des
# images déjà construites.
set -euo pipefail
cd "$(dirname "$0")/.."

PROJECT="${SMOKE_PROJECT:-site-timeo-smoke}"
PORT="${SMOKE_PORT:-8089}"
BASE="http://localhost:$PORT"
JAR="$(mktemp)"
OUT="$(mktemp)"

compose() { APP_PORT="$PORT" docker compose -p "$PROJECT" "$@"; }

cleanup() {
  local status=$?
  if [ "$status" -ne 0 ]; then
    echo
    echo "--- Derniers logs"
    compose logs --tail 40 || true
  fi
  compose down -v --remove-orphans >/dev/null 2>&1 || true
  rm -f "$JAR" "$OUT"
  exit "$status"
}
trap cleanup EXIT

step() { printf '\n▶ %s\n' "$*"; }
fail() {
  echo "ÉCHEC : $*" >&2
  exit 1
}

# request MÉTHODE CHEMIN [JSON] : affiche le code HTTP, le corps va dans $OUT.
request() {
  local args=(-s -o "$OUT" -w '%{http_code}' -b "$JAR" -c "$JAR" -X "$1" "$BASE$2")
  if [ -n "${3:-}" ]; then args+=(-H 'Content-Type: application/json' -d "$3"); fi
  curl "${args[@]}" || true
}

# expect CODE MÉTHODE CHEMIN [JSON]
expect() {
  local code=$1 got
  shift
  got=$(request "$@")
  [ "$got" = "$code" ] || fail "$1 $2 : HTTP $got au lieu de $code ($(head -c 300 "$OUT"))"
  echo "  ok  $1 $2 → $code"
}

# wait_for CHEMIN CODE : attend jusqu'à 60 s que l'adresse réponde ce code.
wait_for() {
  local code=""
  for _ in $(seq 1 60); do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE$1" || true)
    if [ "$code" = "$2" ]; then
      echo "  ok  $1 → $2"
      return 0
    fi
    sleep 1
  done
  fail "$1 répond $code au lieu de $2 après 60 s"
}

start() {
  local build=(--build)
  if [ "${SMOKE_BUILD:-1}" = "0" ]; then build=(); fi
  compose up -d --wait --wait-timeout 180 "${build[@]}"
}

step "Fichier docker-compose.yml valide"
compose config -q

step "Construction et démarrage (port $PORT)"
compose down -v --remove-orphans >/dev/null 2>&1 || true
start
wait_for /api/health 200
wait_for / 200
grep -q 'id="root"' <(curl -s "$BASE/") || fail "la page d'accueil ne contient pas l'application"

step "Migrations à jour avec les modèles"
compose exec -T backend alembic check

step "Compte : inscription, déconnexion, connexion, photo"
expect 201 POST /api/auth/register '{"username":"fumee","password":"motdepasse"}'
expect 200 GET /api/auth/me
expect 204 POST /api/auth/logout
expect 401 GET /api/auth/me
expect 401 POST /api/auth/login '{"username":"fumee","password":"mauvais!!"}'
expect 200 POST /api/auth/login '{"username":"fumee","password":"motdepasse"}'
# Plus petit PNG valide (1 × 1 pixel), envoyé tel quel comme le fait le frontend.
printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82' >"$OUT.png"
code=$(curl -s -o "$OUT" -w '%{http_code}' -b "$JAR" -X PUT -H 'Content-Type: image/png' \
  --data-binary @"$OUT.png" "$BASE/api/account/avatar" || true)
rm -f "$OUT.png"
[ "$code" = "200" ] || fail "envoi de la photo : HTTP $code ($(head -c 300 "$OUT"))"
echo "  ok  PUT /api/account/avatar → 200"
expect 204 POST /api/auth/logout

step "Visiteur : entrée puis suppression à la déconnexion"
expect 201 POST /api/auth/guest '{"username":"visiteur_fumee"}'
expect 204 POST /api/auth/logout
expect 201 POST /api/auth/guest '{"username":"visiteur_fumee"}'
expect 204 POST /api/auth/logout

step "nginx démarre même si le backend est arrêté"
compose stop backend
compose restart frontend
wait_for / 200
wait_for /api/health 502
compose start backend
# Le frontend n'est pas relancé : il doit retrouver le backend tout seul.
wait_for /api/health 200

step "Les données survivent à un redémarrage complet"
compose down
SMOKE_BUILD=0 start
wait_for /api/health 200
expect 200 POST /api/auth/login '{"username":"fumee","password":"motdepasse"}'

printf '\n✔ Test de fumée réussi\n'
