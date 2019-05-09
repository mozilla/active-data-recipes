#!/usr/bin/env sh

_log() {
    echo $1 >> completion.log
}

_adr_completion() {
    local cur items targets
    COMPREPLY=()

    if [[ $COMP_LINE == *" query"* ]]; then
        items=$(python -c "from adr import sources; print(' '.join(sources.queries))")
    else
        items=$(python -c "from adr import sources; print(' '.join(sources.recipes))")
    fi

    for name in $items
    do
        if [[ $COMP_LINE == *"$name "* ]]; then
            return
        fi

        targets="$targets $name"
    done

    cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=( $(compgen -W "$targets" -- ${cur}) )
}

complete -F _adr_completion adr
