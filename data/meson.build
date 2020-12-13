pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

gnome = import('gnome')

gnome.compile_resources('nino',
  'nino.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: configure_file(
    input: 'about.ui.in',
    output: 'about.ui',
    configuration: conf
  )
)

desktop_file = i18n.merge_file(
  input: 'com.github.mikacousin.nino.desktop.in',
  output: 'com.github.mikacousin.nino.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

install_subdir('fixtures', install_dir: pkgdatadir)

subdir('icons')
