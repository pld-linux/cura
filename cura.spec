Summary:	3D printer control software
Name:		cura
Version:	15.02.1
Release:	0.1
Group:		Applications/Engineering
# Code is AGPLv3
# Icons AGPLv3 https://github.com/daid/Cura/issues/231#issuecomment-12209683
# Example models are CC-BY-SA
# TweakAtZ.py is CC-BY-SA
License:	AGPLv3 and CC-BY-SA
URL:		http://daid.github.com/Cura/
Source0:	https://github.com/daid/Cura/archive/%{version}.tar.gz
# Source0-md5:	f41ba365e5b98907cf55fc70e056c2e8
Source1:	%{name}
Source2:	%{name}.desktop
# UltimakerPlatforms STLs were stripped from the tarball, don't crash because of that
Patch0:		%{name}-dont-show-nc-stls.patch
# Use system paths
Patch1:		%{name}-system-paths.patch
# Rework the logic of determining the version (didn't work)
Patch2:		%{name}-version.patch
Patch3:		%{name}-no-firmware.patch
Patch4:		%{name}-newlines.patch
BuildRequires:	desktop-file-utils
BuildRequires:	dos2unix
BuildRequires:	gettext
BuildRequires:	python-devel
Requires:	CuraEngine >= 14.12.1
Requires:	pypy
Requires:	python-PyOpenGL
Requires:	python-numpy
Requires:	python-power
Requires:	python-serial
Requires:	wxPython
BuildArch:	noarch

%description
Cura is a project which aims to be an single software solution for 3D
printing. While it is developed to be used with the Ultimaker 3D
printer, it can be used with other RepRap based designs.

Cura helps you to setup an Ultimaker, shows your 3D model, allows for
scaling / positioning, can slice the model to G-Code, with sane
editable configuration settings and send this G-Code to the 3D printer
for printing.

%prep
%setup -qn Cura-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

# Use free UltimakerHandle.stl instead of UltimakerRobot_support.stl
FILES=$(grep -Ir "UltimakerRobot_support.stl" . | cut -f1 -d: | sort | uniq | grep -v Attribution.txt | tr '\n' ' ')
sed -i 's/UltimakerRobot_support.stl/UltimakerHandle.stl/g' $FILES

dos2unix resources/example/Attribution.txt

sed -i 's/REPLACE_THIS_IN_SPEC/%{version}/' Cura/util/version.py

mv resources/locale/{zh,zh_CN}
rm -rf resources/locale/po

%build
# rebuild locales
cd resources/locale
rm *.in *.pot
for FILE in *
  do msgfmt $FILE/LC_MESSAGES/Cura.po -o $FILE/LC_MESSAGES/Cura.mo
  rm $FILE/LC_MESSAGES/Cura.po
done
cd -

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{py_sitescriptdir}/Cura
install -d $RPM_BUILD_ROOT%{_datadir}/%{name}/firmware
install -d $RPM_BUILD_ROOT%{_pixmapsdir}
install -d $RPM_BUILD_ROOT%{_localedir}
install -d $RPM_BUILD_ROOT%{_bindir}

cp -apr Cura/* $RPM_BUILD_ROOT%{py_sitescriptdir}/Cura
rm -rf $RPM_BUILD_ROOT%{py_sitescriptdir}/Cura/LICENSE
cp -apr resources/* $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -apr plugins $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -ap %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}
ln -s %{_datadir}/%{name} $RPM_BUILD_ROOT%{py_sitescriptdir}/Cura/resources
ln -s %{_datadir}/%{name}/%{name}.ico $RPM_BUILD_ROOT%{_pixmapsdir}

# locales
cp -a $RPM_BUILD_ROOT%{_datadir}/%{name}/locale/* $RPM_BUILD_ROOT%{_localedir}
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}/locale
ln -s -f %{_localedir}/ $RPM_BUILD_ROOT%{_datadir}/%{name}/ # the app expects the locale folder in here

desktop-file-install --dir=$RPM_BUILD_ROOT%{_desktopdir} %{SOURCE2}

%{find_lang} Cura

%clean
rm -rf $RPM_BUILD_ROOT

%files -f Cura.lang
%defattr(644,root,root,755)
%doc Cura/LICENSE resources/example/Attribution.txt
%{py_sitescriptdir}/Cura
%{_datadir}/%{name}
%{_pixmapsdir}/%{name}.ico
%{_desktopdir}/%{name}.desktop
%attr(755,root,root) %{_bindir}/%{name}
