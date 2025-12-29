#!/bin/bash
# Script complet et corrigé pour préparer tous les Labs et le Projet Final pour Quartz

CONTENT_DIR="content"
LABS=("lab1-practice" "lab2-practice" "lab3-practice")
PROJECT_DIR="projet-final"

prepare_dir() {
    local target_dir="$1"
    mkdir -p "$target_dir/assets"
    echo "Dossier $target_dir préparé avec assets/"
}

convert_notebook() {
    local notebook_path="$1"
    local output_html="$2"
    jupyter nbconvert "$notebook_path" --to html --output "$output_html" --output-dir="$(pwd)"
    echo "Notebook $notebook_path converti en $output_html"
}

copy_assets() {
    local source_dir="$1"
    local target_dir="$2/assets"

    [ -d "$source_dir/proof" ] && cp -r "$source_dir/proof/"* "$target_dir/"
    [ -d "$source_dir/outputs" ] && cp -r "$source_dir/outputs/"* "$target_dir/"

    for f in "$source_dir"/*; do
        if [[ -f "$f" && $f != *.ipynb && $f != proof && $f != outputs ]]; then
            cp "$f" "$target_dir/"
        fi
    done

    echo "Assets copiés de $source_dir vers $target_dir"
}

generate_index_md() {
    local target_dir="$1"
    local title="$2"
    local html_file="$3"

    cat > "$target_dir/index.md" <<EOL
---
title: $title
---

# $title

<iframe src="./$html_file" width="100%" height="900px"></iframe>


## Proof / Outputs
EOL

    # Images
    for img in "$target_dir"/assets/*; do
        [ -f "$img" ] || continue
        ext="${img##*.}"
        if [[ "$ext" == "png" || "$ext" == "jpg" || "$ext" == "jpeg" || "$ext" == "gif" ]]; then
            img_name=$(basename "$img")
            echo "- ![${img_name}](assets/${img_name})" >> "$target_dir/index.md"
        fi
    done

    echo -e "\n### Text files" >> "$target_dir/index.md"

    # TXT / MD files
    for txt in "$target_dir"/assets/*; do
        [ -f "$txt" ] || continue
        ext="${txt##*.}"
        if [[ "$ext" == "txt" || "$ext" == "md" ]]; then
            txt_name=$(basename "$txt")
            echo "- [${txt_name}](assets/${txt_name})" >> "$target_dir/index.md"
        fi
    done

    echo "index.md généré pour $target_dir"
}

# Traitement des Labs
for lab in "${LABS[@]}"; do
    if [ ! -d "$lab" ]; then
        echo "⚠️ Dossier $lab introuvable, passage au suivant"
        continue
    fi

    target_lab_dir="$CONTENT_DIR/labs/${lab%-practice}"
    prepare_dir "$target_lab_dir"

    notebook_file=$(find "$lab" -maxdepth 1 -name '*.ipynb' | head -n 1)
    if [ -z "$notebook_file" ]; then
        echo "⚠️ Aucun notebook trouvé dans $lab, passage au suivant"
        continue
    fi

    notebook_html="${lab%-practice}.html"
    convert_notebook "$notebook_file" "$notebook_html"
    cp "$notebook_html" "$target_lab_dir/"

    copy_assets "$lab" "$target_lab_dir"
    generate_index_md "$target_lab_dir" "Lab ${lab:3:1} – Data Engineering" "$target_lab_dir/$notebook_html"
done

# Traitement du Projet Final
if [ ! -d "$PROJECT_DIR" ]; then
    echo "⚠️ Dossier $PROJECT_DIR introuvable, le script ne peut pas continuer"
    exit 1
fi

project_target_dir="$CONTENT_DIR/project"
prepare_dir "$project_target_dir"

project_notebook=$(find "$PROJECT_DIR" -maxdepth 1 -name '*.ipynb' | head -n 1)
if [ -z "$project_notebook" ]; then
    echo "⚠️ Aucun notebook trouvé dans $PROJECT_DIR, sortie"
    exit 1
fi

convert_notebook "$project_notebook" "project.html"
cp "project.html" "$project_target_dir/"

copy_assets "$PROJECT_DIR" "$project_target_dir"
generate_index_md "$project_target_dir" "Final Project – Data Engineering 1" "$project_target_dir/project.html"

echo -e "\n✅ Tous les labs et le projet final ont été préparés pour Quartz !"

