#!/usr/bin/env bash
# Prove committed HEAD, not the caller's dirty working tree. No repository mounts.
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo"
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo 'Commit tracked changes before verifying the exact HEAD.' >&2
    exit 2
fi
evidence="$repo/artifacts/container"
mkdir -p "$evidence"
git rev-parse HEAD > "$evidence/tested-commit.txt"
# Build environment definition must also be the committed version.
git archive HEAD docker | tar -x -C "$evidence"
docker build -t dungeoncarlemon-foundation "$evidence/docker" > "$evidence/image-build.log" 2>&1
docker image inspect dungeoncarlemon-foundation > "$evidence/image-inspect.json"
container=$(docker create -i dungeoncarlemon-foundation bash -c '
    set -euo pipefail
    tar -x -C /build
    cd /build
    bash scripts/verify-foundation-in-container.sh
')
cleanup() { docker rm "$container" >/dev/null; }
trap cleanup EXIT
status=0
git archive HEAD | docker start -ai "$container" > "$evidence/run.log" 2>&1 || status=$?
container_status=$(docker inspect --format '{{.State.ExitCode}}' "$container")
if [[ $container_status -ne 0 ]]; then status=$container_status; fi
# Copy scoped review evidence only, never the ROM or compiled harness.
for name in packages.tsv setup.log build.log compare.log rom.sha256 build-driver.log; do
    docker cp "$container:/build/artifacts/$name" "$evidence/$name" 2>> "$evidence/run.log" || true
done
docker cp "$container:/build/artifacts/boot/." "$evidence/" 2>> "$evidence/run.log" || true
if [[ $status -ne 0 ]]; then
    echo "Container validation failed (exit $status). See $evidence" >&2
    exit "$status"
fi
test -s "$evidence/new-game.png"
grep -q 'pokeemerald.gba: OK' "$evidence/compare.log"
grep -q 'frame=2044 keys=0 capture=new-game.ppm' "$evidence/boot.log"
echo "Build/boot route completed. Visually review title.png, menu.png and new-game.png in $evidence."
