Summary:	3D printer control software
Summary(pl.UTF-8):	Oprogramowanie do sterowania drukarkami 3D
Name:		cura
# keep in sync with CuraEngine, libArgus, libSavitar, python3-Uranium
Version:	4.13.2
Release:	
Epoch:		1
Group:		Applications/Engineering
# Code is AGPLv3
# Icons AGPLv3 https://github.com/daid/Cura/issues/231#issuecomment-12209683
# Example models are CC-BY-SA
# TweakAtZ.py is CC-BY-SA
License:	AGPL v3 and CC-BY-SA
Source0:	https://github.com/Ultimaker/Cura/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	57405484fd44518dff522cc205fbf548
Source1:	https://github.com/Ultimaker/fdm_materials/archive/%{version}/fdm_materials-%{version}.tar.gz
# Source1-md5:	db985047a2f859a77cb7c2468e2e0bbf
Patch0:		plugins-path.patch
URL:		https://ultimaker.com/en/products/cura-software
BuildRequires:	cmake >= 3.6
BuildRequires:	desktop-file-utils
BuildRequires:	gettext
BuildRequires:	gettext-tools
# UraniumTranslationTools
BuildRequires:	python3-Uranium = %{version}
BuildRequires:	python3-devel >= 1:3.5
BuildRequires:	python3-pytest
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.219
Requires:	CuraEngine = %{epoch}:%{version}
Requires:	Qt5Quick-controls >= 5.6.0
Requires:	fonts-TTF-OpenSans
Requires:	python3-PyQt5 >= 5.6.0
Requires:	python3-Uranium = %{version}
# for FirmwareUpdateChecker plugin
Requires:	python3-certifi
Requires:	python3-numpy
# for 3MFReader and 3MFWriter plugins
Requires:	python3-savitar = %{version}
Requires:	python3-serial
Requires:	python3-zeroconf
# TODO:
# for UFPReader and UFPWriter plugins
#Requires:	python3-charon
# for AMFReader and TrimeshReader plugins
#Requires:	python3-trimesh
# for SentryLogger plugin
#Requires:	python3-sentry_sdk
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

%description -l pl.UTF-8
Cura to projekt, który ma być kompletnym oprogramowaniem do drukowania
3D. Choć jest tworzony do użytku z drukarką Ultimaker 3D, może być
używany także z innymi projektami opartymi na RepRap.

Cura pomaga skonfigurować drukarkę Ultimaker, pokazuje model 3D,
pozwala go skalować/pozycjonować, dzielić go na G-kod z rozsądnymi
modyfikowalnymi ustawieniami i wysyłać go do drukarki 3D.

%prep
%setup -q -n Cura-%{version} -a1
%patch0 -p1

for bad_lang in cs_CZ de_DE es_ES fi_FI fr_FR hu_HU it_IT ja_JP ko_KR nl_NL pl_PL pt_PT ru_RU tr_TR ; do
	lang="$(echo $bad_lang | sed 's/_.*//')"
	%{__mv} "resources/i18n/$bad_lang" "resources/i18n/$lang"
done

# Upstream installs to lib/python3/dist-packages
# We want to install to %{py3_sitescriptdir}
%{__sed} -i 's|lib${LIB_SUFFIX}/python${Python3_VERSION_MAJOR}.*/.*-packages|%(echo %{py3_sitescriptdir} | sed -e s@%{_prefix}/@@)|g' CMakeLists.txt

# Adjust shebang
%{__sed} -i '1s=/usr/bin/env python3=%{__python3}=' cura_app.py

%build
mkdir build
cd build
%cmake .. \
	-DCURA_VERSION:STRING=%{version}

%{__make}

cd ../fdm_materials-%{version}
mkdir build
cd build
%cmake ..

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

%{__make} -C fdm_materials-%{version}/build install \
	DESTDIR=$RPM_BUILD_ROOT

# Sanitize the location of locale files
%{__mv} $RPM_BUILD_ROOT%{_datadir}/{cura/resources/i18n,locale}
ln -s ../../locale $RPM_BUILD_ROOT%{_datadir}/cura/resources/i18n
%{__rm} $RPM_BUILD_ROOT%{_localedir}/*/*.po
%{__rm} $RPM_BUILD_ROOT%{_localedir}/*.pot

%find_lang cura --all-name

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_icon_cache hicolor

%postun
%update_icon_cache hicolor

%files -f cura.lang
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_bindir}/cura
%{py3_sitescriptdir}/cura
%{_datadir}/%{name}
%{_datadir}/metainfo/com.ultimaker.cura.appdata.xml
%{_datadir}/mime/packages/cura.xml
%{_desktopdir}/com.ultimaker.cura.desktop
%{_iconsdir}/hicolor/*x*/apps/cura-icon.png
