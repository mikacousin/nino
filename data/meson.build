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

install_subdir('fixtures', install_dir: pkgdatadir)
