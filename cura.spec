Summary:	3D printer control software
Name:		cura
Version:	3.5.1
Release:	2
Epoch:		1
Group:		Applications/Engineering
# Code is AGPLv3
# Icons AGPLv3 https://github.com/daid/Cura/issues/231#issuecomment-12209683
# Example models are CC-BY-SA
# TweakAtZ.py is CC-BY-SA
License:	AGPLv3 and CC-BY-SA
Source0:	https://github.com/Ultimaker/Cura/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	a8b1de1bb8cfc043aa1d742f2cc78911
Source1:	https://github.com/Ultimaker/fdm_materials/archive/%{version}/fdm_materials-%{version}.tar.gz
# Source1-md5:	7d0bcfe67173f8fd616ac5ca55eb815b
Patch0:		plugins-path.patch
URL:		https://ultimaker.com/en/products/cura-software
BuildRequires:	cmake
BuildRequires:	desktop-file-utils
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
Requires:	python3-Uranium = %{version}
Requires:	python3-numpy
Requires:	python3-power
Requires:	python3-savitar >= 2.7.0
Requires:	python3-serial
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
%setup -q -n Cura-%{version} -a1
%patch0 -p1

for bad_lang in de_DE es_ES fi_FI fr_FR it_IT ja_JP ko_KR nl_NL pl_PL pt_PT ru_RU tr_TR ; do
	lang="$(echo $bad_lang | sed 's/_.*//')"
	%{__mv} "resources/i18n/$bad_lang" "resources/i18n/$lang"
done

# The setup.py is only useful for py2exe, remove it, so noone is tempted to use it
%{__rm} setup.py

# Upstream installs to lib/python3/dist-packages
# We want to install to %{py3_sitescriptdir}
%{__sed} -i 's|lib${LIB_SUFFIX}/python${PYTHON_VERSION_MAJOR}.*/.*-packages|%(echo %{py3_sitescriptdir} | sed -e s@%{_prefix}/@@)|g' CMakeLists.txt

# Wrong shebang
%{__sed} -i '1s=^#!%{_bindir}/\(python\|env python\)3*=#!%{__python3}=' cura_app.py

%build
mkdir build
cd build
%{cmake} .. \
	-DCURA_VERSION:STRING=%{version}

%{__make}

cd ../fdm_materials-%{version}
mkdir build
cd build
%{cmake} ..

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install DESTDIR=$RPM_BUILD_ROOT
%{__make} -C fdm_materials-%{version}/build install DESTDIR=$RPM_BUILD_ROOT

# Sanitize the location of locale files
%{__mv} $RPM_BUILD_ROOT%{_datadir}/{cura/resources/i18n,locale}
ln -s ../../locale $RPM_BUILD_ROOT%{_datadir}/cura/resources/i18n
%{__rm} $RPM_BUILD_ROOT%{_localedir}/*/*.po
%{__rm} $RPM_BUILD_ROOT%{_localedir}/*.pot

%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}
%py_postclean

%find_lang cura --all-name

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_icon_cache hicolor

%postun
%update_icon_cache hicolor

%files -f cura.lang
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/%{name}
%{py3_sitescriptdir}/cura
%{_desktopdir}/%{name}.desktop
%{_datadir}/%{name}
%{_datadir}/metainfo/cura.appdata.xml
%{_datadir}/mime/packages/cura.xml
%{_iconsdir}/hicolor/*x*/apps/cura-icon.png
