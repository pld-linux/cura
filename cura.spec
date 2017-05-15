#
# TODO: find out why all Ultimaker printers later than 2 cannot be added
#
Summary:	3D printer control software
Name:		cura
Version:	2.5.0
Release:	2
Epoch:		1
Group:		Applications/Engineering
# Code is AGPLv3
# Icons AGPLv3 https://github.com/daid/Cura/issues/231#issuecomment-12209683
# Example models are CC-BY-SA
# TweakAtZ.py is CC-BY-SA
License:	AGPLv3 and CC-BY-SA
Source0:	https://github.com/Ultimaker/Cura/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	ebe1b78c8b9ce77c289a266c9e732dc8
Source1:	%{name}
Patch0:		plugins-path.patch
URL:		https://ultimaker.com/en/products/cura-software
BuildRequires:	cmake
BuildRequires:	desktop-file-utils
BuildRequires:	dos2unix
BuildRequires:	gettext
BuildRequires:	gettext-tools
BuildRequires:	python3-Uranium = %{version}
BuildRequires:	python3-devel
BuildRequires:	python3-pytest
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.219
Requires:	CuraEngine = %{epoch}:%{version}
Requires:	Qt5Quick-controls
Requires:	fonts-TTF-OpenSans
Requires:	python3-PyOpenGL
Requires:	python3-PyQt5
Requires:	python3-numpy
Requires:	python3-power
Requires:	python3-savitar
Requires:	python3-serial
Requires:	python3-Uranium = %{version}
Requires:	python3-zeroconf
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Cura is a project which aims to be an single software solution for 3D
printing. While it is developed to be used with the Ultimaker 3D
printer, it can be used with other RepRap based designs.

Cura helps you to setup an Ultimaker, shows your 3D model, allows for
scaling / positioning, can slice the model to G-Code, with sane
editable configuration settings and send this G-Code to the 3D printer
for printing.

%prep
%setup -q -n Cura-%{version}
%patch0 -p1

# The setup.py is only useful for py2exe, remove it, so noone is tempted to use it
rm setup.py

# https://github.com/Ultimaker/Cura/issues/1784
sed -i 's/Version=1/Version=1.1/' cura.desktop.in

# Upstream installs to lib/python3/dist-packages
# We want to install to %%{py3_sitescriptdir}
sed -i 's|lib/python${PYTHON_VERSION_MAJOR}/dist-packages|%(echo %{py3_sitescriptdir} | sed -e s@%{_prefix}/@@)|g' CMakeLists.txt

# Wrong end of line encoding
dos2unix docs/How_to_use_the_flame_graph_profiler.md

# Wrong shebang
sed -i '1s=^#!%{_bindir}/\(python\|env python\)3*=#!%{__python3}=' cura_app.py

# Invalid locale name ptbr
# https://github.com/Ultimaker/Uranium/issues/246
mv resources/i18n/{ptbr,pt_BR}
sed -i 's/"Language: ptbr\\n"/"Language: pt_BR\\n"/' resources/i18n/pt_BR/*.po

mv resources/i18n/{jp,ja}
sed -i 's/"Language: jp\\n"/"Language: ja\\n"/' resources/i18n/ja/*.po

# Failing test, mixes sets and lists :(
# Changed in master, not reporting to upstream
sed -i -e '0,/set()/{s/set()/[]/}' \
       -e 's/{/[/g' \
       -e 's/}/]/g' \
    tests/TestMachineAction.py

%build
mkdir build
cd build
%{cmake} .. \
	-DCURA_VERSION:STRING=%{version}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C build install DESTDIR=$RPM_BUILD_ROOT

# Sanitize the location of locale files
mv $RPM_BUILD_ROOT%{_datadir}/{cura/resources/i18n,locale}
ln -s ../../locale $RPM_BUILD_ROOT%{_datadir}/cura/resources/i18n
rm $RPM_BUILD_ROOT%{_localedir}/*/*.po
rm $RPM_BUILD_ROOT%{_localedir}/*.pot

# Unbundle fonts
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}/resources/themes/cura/fonts/
ln -s %{_datadir}/fonts/open-sans/ $RPM_BUILD_ROOT%{_datadir}/%{name}/resources/themes/cura/fonts

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean

%find_lang cura --all-name

%clean
rm -rf $RPM_BUILD_ROOT

%files -f cura.lang
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{name}
%{py3_sitescriptdir}/cura
%{_desktopdir}/%{name}.desktop
%{_datadir}/%{name}
%{_datadir}/appdata/cura.appdata.xml
%{_datadir}/mime/packages/cura.xml
