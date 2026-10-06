#!/usr/bin/env bash
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
cache=${DCC_CACHE:-"$repo/.cache"}
mkdir -p "$cache"
assert_clean_cache() {
    local dest=$1
    if [[ -d "$dest/.git" ]] && [[ -n "$(git -C "$dest" status --porcelain --untracked-files=all)" ]]; then
        echo "Refusing dirty source cache: $dest. Preserve changes and use a separate DCC_CACHE." >&2
        return 1
    fi
}
# Check both before fetching, checking out, hydrating inputs or building anything.
assert_clean_cache "$cache/pokeemerald"
assert_clean_cache "$cache/agbcc"
pin_repo() {
    local url=$1 dest=$2 revision=$3
    if [[ ! -d "$dest/.git" ]]; then
        git clone --no-checkout "$url" "$dest"
    fi
    git -C "$dest" fetch origin "$revision"
    git -C "$dest" checkout --detach "$revision"
    test "$(git -C "$dest" rev-parse HEAD)" = "$revision"
    assert_clean_cache "$dest"
}
pin_repo https://github.com/pret/pokeemerald.git "$cache/pokeemerald" 731ad5bfd6e6f265508d0efcca0ba42f9dcf5881
pin_repo https://github.com/pret/agbcc.git "$cache/agbcc" da598c1d918402c42c0c0d7128ba14567f3175e9
# Upstream's three multiboot inputs are needed for a matching baseline, but are
# intentionally not committed in this repository. Verify Git blob identity.
while read -r blob path; do
    git -C "$cache/pokeemerald" show "HEAD:$path" > "$repo/engine/$path"
    test "$(git hash-object "$repo/engine/$path")" = "$blob"
done <<'INPUTS'
0afff07f5d2314e2bd35d99de518cbc114009b5e data/mb_berry_fix.gba
fdeb854a054ba02191f6a209ec5b649f21c4e335 data/mb_colosseum.gba
85057cf4e2bd657da5d632ac12d1ea24aeaa4499 data/mb_ereader.gba
INPUTS
(cd "$cache/agbcc" && bash ./build.sh && ./install.sh "$repo/engine")
