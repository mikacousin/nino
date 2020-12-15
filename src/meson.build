moduledir = join_paths(pkgdatadir, 'nino')
gnome = import('gnome')

python = import('python')

configure_file(
  input: 'nino.in',
  output: 'nino',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

configure_file(
  input: 'paths.py.in',
  output: 'paths.py',
  configuration: conf,
  install: true,
  install_dir: join_paths(python_dir, 'nino')
)

nino_sources = [
  'application.py',
  'console.py',
  'defines.py',
  'device.py',
  'fixture.py',
  'patch.py',
  'settings.py',
  'shortcuts.py',
  'signals.py',
  'tab_live.py',
  'tab_patch.py',
  'undo_redo.py',
  'widgets_channel.py',
  'widgets_output.py',
  'window_live.py',
  'window_playback.py',
]

install_data(
  nino_sources,
  install_dir: join_paths(python_dir, 'nino')
)
