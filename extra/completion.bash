#!/usr/bin/env sh

_log() {
    echo $1 >> completion.log
}

_adr_completion() {
    local cur dir ext targets
    COMPREPLY=()

    dir="$PWD/adr"
    if [[ $COMP_LINE == *" query"* ]]; then
        dir="$dir/queries"
        ext="query"
    else
        dir="$dir/recipes"
        ext="py"
    fi

    for name in $dir/*
    do
        name=${name##*/}
        if [[ $name == *.$ext && $name != "_"* ]]; then
            name=${name%.*}

            if [[ $COMP_LINE == *"$name "* ]]; then
                return
            fi

            targets="$targets $name"
        fi
    done

    cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=( $(compgen -W "$targets" -- ${cur}) )
}

complete -F _adr_completion adr
