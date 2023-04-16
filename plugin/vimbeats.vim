if exists('g:spotify')
    finish
endif
let g:spotify = 1

let s:script_name = '/script.py'

function! vimbeats#Run(...) abort
    let l:plugindir = expand('<sfile>:p:h')
    let l:script = plugindir . s:script_name
    let l:cmd =  script . ' ' . join(a:000, ' ')
    call system(cmd)
endfunction

let s:play_toggle = 1
let s:device_id = '012013d1f70ef84ba5a7bb25dfb8b7a5ea852064'
function! vimbeats#ToggleSpotify()
    if s:play_toggle
        echo 'Pausing spotify'
        call vimbeats#Run('pause')
        let s:play_toggle = 0
    else
        echo 'Playing spotify'
        if exists('s:device_id')
            call vimbeats#Run('play', '-d', s:device_id)
        else
            call vimbeats#Run('play')
        endif
        let s:play_toggle = 1
    endif
endfunction

function! vimbeats#Next()
    echo "Playing next song"
    silent call vimbeats#Run('next')
endfunction

function! vimbeats#Prev()
    echo "Playing previous song"
    silent call vimbeats#Run('prev')
endfunction

function! vimbeats#PlayContext(context_id, context_name)
    if a:context_id==?""
        echo "Error: Missing context id!"
        return
    endif

    if a:context_name!=#""
        echo "Playing ".a:context_name
    else
        echo a:context_name
        echo "error"
    endif

    if exists('s:device_id')
        call vimbeats#Run('play', '-d', s:device_id, '-c', a:context_id)
    else
        call vimbeats#Run('play', '-c', a:context_id)
    endif
endfunction
