" ####### Auto Completion
" let g:gutentags_modules = ['ctags']
let g:gutentags_modules = []

" on save
let b:enable_rsync = 1

" " VNC server
" let b:rsync_server = "pi-church"
" let b:rsync_remote = "~/src/midiController"

" VNC server
let b:rsync_server = "pi"
let b:rsync_remote = "~/src/midiController"

" " VNC server
" let b:rsync_server = "micropi"
" let b:rsync_remote = "~/src/midiController"

" DON't end with forward slash
let b:rsync_local = "/home/hle/src/midiController"
let b:rsync_exclude = ".project/rsync_exclude"
