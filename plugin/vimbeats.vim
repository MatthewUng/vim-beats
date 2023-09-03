if exists('g:spotify')
    finish
endif
let g:spotify = 1

let s:script_name = '/script.py'
let s:plugindir = expand('<sfile>:p:h:h')
let s:queue_choices = {}

function! vimbeats#Run(...) abort
    let l:script = s:plugindir . s:script_name
    let l:cmd =  l:script . ' ' . join(a:000, ' ')
    let l:out = system('python3 '.cmd)
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

function! vimbeats#PlayContext(context_id)
    if exists('s:device_id')
        call vimbeats#Run('play', '-d', s:device_id, '-c', a:context_id)
    else
        call vimbeats#Run('play', '-c', a:context_id)
    endif

    " Attempt to print playlist name if context is a playlist
    let l:PLAYLIST_PREFIX = 'spotify:playlist:'
    if a:context_id[0:len(l:PLAYLIST_PREFIX)-1] ==# l:PLAYLIST_PREFIX
        echo "Playing " .. vimbeats#Run('get-playlist', '-c', a:context_id)
    endif
endfunction

function! vimbeats#Queue(track_id)
    call vimbeats#Run('queue-song -c ' . a:track_id)
endfunction

" Helper callback method for `SearchAndQueue`
function! vimbeats#ReceiveQueryResults(search_choice)
    call vimbeats#Queue(s:queue_choices[a:search_choice])
    echom 'Queued: ' . a:search_choice
endfunction

function! vimbeats#SearchAndQueue(query)
    " clear dictionary
    call filter(s:queue_choices, 0)

    let l:resp = vimbeats#Run(" search --query '" . a:query . "'")
    let l:songs = split(l:resp, '\n')
    for song in songs
        let l:pair = split(song, '###')
        let s:queue_choices[l:pair[0]] = l:pair[1]
    endfor

    call fzf#run({'source': s:queue_choices->keys(), 'window': {'width': 0.9, 'height': 0.6}, 'sink': function('vimbeats#ReceiveQueryResults')})
endfunction

" Helper callback method for `SearchAndPlayPlaylists`
function! vimbeats#ReceivePlaylistQueryResults(search_choice)
    call vimbeats#PlayContext('spotify:playlist:' .s:queue_choices[a:search_choice])
endfunction

function! vimbeats#SearchAndPlayPlaylist()
    " clear dictionary
    call filter(s:queue_choices, 0)

    let l:resp = vimbeats#Run('get-playlists')
    let l:songs = split(l:resp, '\n')
    for song in songs
        let l:pair = split(song, '###')
        let s:queue_choices[l:pair[0]] = l:pair[1]
    endfor

    call fzf#run({'source': s:queue_choices->keys(), 'window': {'width': 0.9, 'height': 0.6}, 'sink': function('vimbeats#ReceivePlaylistQueryResults')})
endfunction
