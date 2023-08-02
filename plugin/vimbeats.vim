if exists('g:spotify')
    finish
endif
let g:spotify = 1

let s:script_name = '/script.py'
let s:plugindir = expand('<sfile>:p:h')

function! vimbeats#Run(...) abort
    let l:script = s:plugindir . s:script_name
    let l:cmd =  script . ' ' . join(a:000, ' ')
    let l:out = system(cmd)
    return out
endfunction

function! vimbeats#CurrentlyPlaying() abort
    let l:out = vimbeats#Run('current-song')
    return out
endfunction

let s:play_toggle = 1
function! vimbeats#ToggleSpotify(device_id)
    if s:play_toggle
        echo 'Pausing spotify'
        call vimbeats#Run('pause')
        let s:play_toggle = 0
    else
        if a:device_id!=?""
            call vimbeats#Run('play', '-d', a:device_id)
        else
            call vimbeats#Run('play')
        endif
        echo vimbeats#CurrentlyPlaying()
        let s:play_toggle = 1
    endif
endfunction

function! vimbeats#Next()
    silent call vimbeats#Run('next')
    echo vimbeats#CurrentlyPlaying()
endfunction

function! vimbeats#Prev()
    silent call vimbeats#Run('prev')
    echo vimbeats#CurrentlyPlaying()
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
