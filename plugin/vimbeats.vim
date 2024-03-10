if exists('g:spotify')
    finish
endif
let g:spotify = 1

let s:script_name = '/script.py'
let s:plugindir = expand('<sfile>:p:h:h')
let s:queue_choices = {}

function s:get_preview_command(fname)
    let preview_py = s:plugindir . '/scripts/playlist_preview.py'
    return 'grep {} ' . a:fname . " | python3 " . l:preview_py
endfunction

function! s:getpos()
  return {'tab': tabpagenr(), 'win': winnr(), 'winid': win_getid(), 'cnt': winnr('$'), 'tcnt': tabpagenr('$')}
endfunction

" Configures and creates a popup window
function! s:configure_and_create_popup(width, height) abort
  let xoffset = 0.5
  let yoffset = 0.5

  " Use current window size for positioning relatively positioned popups
  let columns = &columns
  let lines = &lines - has('nvim')

  " Size and position
  let width = min([max([8, float2nr(columns * a:width)]), columns])
  let height = min([max([4, float2nr(lines * a:height)]), lines])
  let row = float2nr(yoffset * (lines - height))
  let col = float2nr(xoffset * (columns - width))

  " Managing the differences
  let row = min([max([0, row]), &lines - has('nvim') - l:height])
  let col = min([max([0, col]), &columns - l:width])

  call s:create_popup({
    \ 'row': row, 'col': col, 'width': width, 'height': height
  \ })
endfunction

" final function to create the selector popup
function! s:create_popup(opts) abort
  let buf = nvim_create_buf(v:false, v:true)
  let opts = extend({'relative': 'editor', 'style': 'minimal'}, a:opts)
  let win = nvim_open_win(buf, v:true, opts)
  silent! call setwinvar(win, '&winhighlight', 'Pmenu:,Normal:Normal')
  call setwinvar(win, '&colorcolumn', '')
endfunction

function! s:execute_cmd_in_term(ctx, command) abort
  let winrest = winrestcmd()
  let pbuf = bufnr('')
  let ppos = s:getpos()
  call s:configure_and_create_popup(0.9, 0.6)

  let fzf = { 'buf': bufnr(''), 'pbuf': pbuf, 'ppos': ppos,
            \ 'winrest': winrest, 'lines': &lines,
            \ 'columns': &columns, 'command': a:command , 'ctx': a:ctx}
  function! fzf.on_exit(id, code, ...)
    if bufexists(self.buf)
      execute 'bd!' self.buf
    endif
    call self.ctx['callback'](self.ctx)
  endfunction

  try
    let command = a:command
    call termopen(command, fzf)
    tnoremap <buffer> <c-z> <nop>
  endtry
  setlocal nospell bufhidden=wipe nobuflisted nonumber
  setf spotify
  startinsert
endfunction

" Produces the run command from an array of arguments
function s:get_run_command(arr) abort
    let l:script = s:plugindir . s:script_name
    let l:cmd =  l:script . ' ' . join(a:arr, ' ')
    return 'python3 '.cmd
endfunction

function! vimbeats#Run(...) abort
    let command = s:get_run_command(a:000)
    let out = system(l:command)
    return l:out
endfunction

function! vimbeats#CurrentlyPlaying() abort
    let l:out = vimbeats#Run('current-song')
    return out
endfunction

let s:play_toggle = 1
function! vimbeats#ToggleSpotify(...)
    if s:play_toggle
        echo 'Pausing spotify'
        call vimbeats#Run('pause')
        let s:play_toggle = 0
    else
        if exists('g:SpotifyDeviceID')
            call vimbeats#Run('play', '-d', g:SpotifyDeviceID)
        elseif a:0 == 1:
            let device_id = a:1
            call vimbeats#Run('play', '-d', l:device_id)
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
    if exists('g:SpotifyDeviceID')
        call vimbeats#Run('play', '-d', g:SpotifyDeviceID, '-c', a:context_id)
    else
        call vimbeats#Run('play', '-c', a:context_id)
    endif

    " Attempt to print playlist name if context is a playlist
    let l:PLAYLIST_PREFIX = 'spotify:playlist:'
    if a:context_id[0:len(l:PLAYLIST_PREFIX)-1] ==# l:PLAYLIST_PREFIX
        let id = a:context_id[len(l:PLAYLIST_PREFIX):]
        echom "Playing " . vimbeats#Run('get-playlist', '-c', a:context_id)
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
        if len(l:pair) < 2
            continue
        endif
        let s:queue_choices[l:pair[0]] = l:pair[1]
    endfor

    call fzf#run({'source': s:queue_choices->keys(), 'window': {'width': 0.9, 'height': 0.6}, 'sink': function('vimbeats#ReceiveQueryResults')})
endfunction

" Helper callback method for `SearchAndPlayPlaylists`
function! vimbeats#ReceivePlaylistQueryResults(search_choice)
    call vimbeats#PlayContext('spotify:playlist:' . s:queue_choices[a:search_choice])
endfunction

function! vimbeats#SearchAndPlayPlaylist()
    let playlist_file = tempname()
    let results_file = tempname()

    let playlist_command = s:get_run_command(['get-playlists']) . ' > ' . playlist_file
    call system(l:playlist_command)

    let command = 'cat ' . playlist_file . ' '
    let command .= "| python3 " . s:plugindir . '/scripts/playlist_names.py '
    let command .= '| fzf --border --prompt ' . "'Playlists>'"
    let command .= ' --preview="' . s:get_preview_command(l:playlist_file) . '" '
    let command .= " > " . results_file

    let ctx = {'results_file': results_file, 'playlist_file': playlist_file}
    let ctx['callback'] = function("PlayPlaylistCallback")
    call s:execute_cmd_in_term(l:ctx, l:command)
endfunction


" Callback for playing a playback
" ctx is a dictionary with two fields
"  * "playlist_file"  - the path of the file for all playlists
"  * "results_file" - the path of the file for the chosen selection
function! PlayPlaylistCallback(ctx)
    let playlist_file = a:ctx['playlist_file']
    let results_file = a:ctx['results_file']
    if getfsize(l:results_file) == 0
        return
    endif

    let playlist_name = readfile(l:results_file)[0]

    let command = 'grep ' . "'" . playlist_name . "'" . ' ' . playlist_file
    let command .= ' | python3 ' . s:plugindir . '/scripts/playlist_id.py'

    let playlist_id = trim(system(command))
    let id = 'spotify:playlist:' . playlist_id

    call vimbeats#PlayContext(id)
endfunction

function! vimbeats#SearchAndPlayFeaturedPlaylist()
    let playlist_file = tempname()
    let results_file = tempname()

    let playlist_command = s:get_run_command(['get-featured-playlists']) . ' > ' . playlist_file
    call system(l:playlist_command)

    let command = 'cat ' . playlist_file . ' '
    let command .= "| python3 " . s:plugindir . '/scripts/playlist_names.py '
    let command .= '| fzf --border --prompt ' . "'Featured>'"
    let command .= ' --preview="' . s:get_preview_command(l:playlist_file) . '" '
    let command .= " > " . results_file

    let ctx = {'results_file': results_file, 'playlist_file': playlist_file}
    let ctx['callback'] = function("PlayPlaylistCallback")
    call s:execute_cmd_in_term(l:ctx, l:command)
endfunction
