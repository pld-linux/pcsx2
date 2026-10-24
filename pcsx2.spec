#
# Conditional build:
%bcond_without	tests		# build without tests
%bcond_without	gsrunner	# build the GSRunner
#
# Current revision for "latest" tag in https://github.com/PCSX2/pcsx2_patches
%define		patches_rev		a44ba70

Summary:	Free and open-source PlayStation 2 (PS2) emulator
Name:		pcsx2
Version:	2.9.144
Release:	0.1
License:	GPL v3
Group:		Applications
Source0:	https://github.com/PCSX2/pcsx2/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	15c71a4ef0fe178016fe5f25d699f70c
Source1:	https://github.com/PCSX2/pcsx2_patches/archive/%{patches_rev}/%{name}_patches-%{patches_rev}.tar.gz
# Source1-md5:	538832b86af372570f77928af8c8049a
Patch0:		shaderc.patch
Patch1:		no-default-build-type.patch
URL:		https://pcsx2.net/
BuildRequires:	KDDockWidgets-devel >= 2.3.0
BuildRequires:	Qt6Core-devel >= 6.10
BuildRequires:	Qt6Gui-devel >= 6.10
BuildRequires:	Qt6Widgets-devel >= 6.10
BuildRequires:	SDL3-devel >= 3.2.6
BuildRequires:	clang
BuildRequires:	cmake >= 3.16
BuildRequires:	curl-devel
BuildRequires:	dbus-devel
# Preferred is 9.0
BuildRequires:	ffmpeg-devel >= 7.1
BuildRequires:	fontconfig-devel
BuildRequires:	freetype-devel >= 2.10
BuildRequires:	libbacktrace-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libpcap-devel
BuildRequires:	libpng-devel >= 1.6.40
BuildRequires:	libwebp-devel >= 1.3.2
BuildRequires:	lld
BuildRequires:	lz4-devel
BuildRequires:	pkgconfig
BuildRequires:	plutosvg-devel >= 0.0.8-2
BuildRequires:	plutovg-devel >= 1.3.3-3
BuildRequires:	qt6-linguist >= 6.10
BuildRequires:	rapidyaml-devel
BuildRequires:	rpmbuild(macros) >= 1.605
BuildRequires:	shaderc-devel
BuildRequires:	udev-devel
BuildRequires:	wayland-devel
BuildRequires:	wayland-egl-devel
BuildRequires:	xorg-lib-libX11-devel
BuildRequires:	xorg-lib-libXrandr-devel
BuildRequires:	zip
BuildRequires:	zlib-devel >= 1.3
BuildRequires:	zstd-devel >= 1.5.5
ExclusiveArch:	%{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		filterout		-fvar-tracking-assignments -Werror=trampolines

%description
PCSX2 is a free and open-source PlayStation 2 (PS2) emulator. Its
purpose is to emulate the PS2's hardware, using a combination of MIPS
CPU Interpreters, Recompilers and a Virtual Machine which manages
hardware states and PS2 system memory. This allows you to play PS2
games on your PC, with many additional features and benefits.

%prep
%setup -q -a1
%patch -P0 -p1
%patch -P1 -p1

%build
export CC="clang"
export CXX="clang++"
export LLVM_PROFDATA="llvm-profdata"
export AR="llvm-ar"
export NM="llvm-nm"
export RANLIB="llvm-ranlib"

%cmake -B build -G Ninja \
	-DBUILD_SHARED_LIBS:BOOL=OFF \
	-DUSE_CLANG:BOOL=ON \
	-DCMAKE_C_COMPILER=clang \
	-DCMAKE_CXX_COMPILER=clang++ \
	-DCMAKE_EXE_LINKER_FLAGS_INIT="-fuse-ld=lld" \
	-DCMAKE_MODULE_LINKER_FLAGS_INIT="-fuse-ld=lld" \
	-DCMAKE_SHARED_LINKER_FLAGS_INIT="-fuse-ld=lld" \
	-DCMAKE_INTERPROCEDURAL_OPTIMIZATION:BOOL=ON \
	%{cmake_on_off tests ENABLE_TESTS} \
	%{cmake_on_off gsrunner ENABLE_GSRUNNER} \
	-DENABLE_QT_UI:BOOL=ON \
	-DPACKAGE_MODE:BOOL=ON \
	-DBUNDLE_EMOJI_FONT:BOOL=ON \
	-DENABLE_SETCAP:BOOL=ON \
	-DUSE_OPENGL:BOOL=ON \
	-DUSE_VULKAN:BOOL=ON \
	-DX11_API:BOOL=ON \
	-DWAYLAND_API:BOOL=ON \
	-DUSE_BACKTRACE:BOOL=ON \
	-DUSE_LINKED_FFMPEG:BOOL=OFF

%ninja_build -C build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/{%{_datadir}/{applications,metainfo},%{_iconsdir}/hicolor/512x512/apps}

%ninja_install -C build

cd pcsx2_patches-%{patches_rev}*/patches
zip $RPM_BUILD_ROOT%{_datadir}/PCSX2/resources/patches.zip *
cd ../..

cp -p .github/workflows/scripts/linux/flatpak/screenshots/screenshot*.png $RPM_BUILD_ROOT%{_datadir}/PCSX2/
cp -p .github/workflows/scripts/linux/pcsx2-qt.desktop $RPM_BUILD_ROOT%{_desktopdir}/net.pcsx2.PCSX2.desktop
cp -p ./bin/resources/icons/AppIconLarge.png $RPM_BUILD_ROOT%{_iconsdir}/hicolor/512x512/apps/PCSX2.png

_DATE=$(stat --printf '%y' .github)
%{__sed} -e 's|https://.*/screenshots/|%{_datadir}/PCSX2/|' \
	-e "s|@GIT_VERSION@|%{version}}|" \
	-e "s|@GIT_DATE@|${_DATE}|" \
	-e "s|@GIT_HASH@|v%{version}|" \
	.github/workflows/scripts/linux/pcsx2-qt.metainfo.xml.in > \
	$RPM_BUILD_ROOT%{_datadir}/metainfo/net.pcsx2.PCSX2.appdata.xml

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_bindir}/pcsx2-gsrunner
%attr(755,root,root) %{_bindir}/pcsx2-qt
%{_desktopdir}/net.pcsx2.PCSX2.desktop
%{_iconsdir}/hicolor/512x512/apps/PCSX2.png
%{_datadir}/metainfo/net.pcsx2.PCSX2.appdata.xml
%dir %{_datadir}/PCSX2
%{_datadir}/PCSX2/resources
%{_datadir}/PCSX2/screenshot*.png
%dir %{_datadir}/PCSX2/translations
%lang(af) %{_datadir}/PCSX2/translations/pcsx2-qt_af-ZA.qm
%lang(ar) %{_datadir}/PCSX2/translations/pcsx2-qt_ar-SA.qm
%lang(az) %{_datadir}/PCSX2/translations/pcsx2-qt_az-AZ.qm
%lang(bg) %{_datadir}/PCSX2/translations/pcsx2-qt_bg-BG.qm
%lang(ca) %{_datadir}/PCSX2/translations/pcsx2-qt_ca-ES.qm
%lang(cs) %{_datadir}/PCSX2/translations/pcsx2-qt_cs-CZ.qm
%lang(da) %{_datadir}/PCSX2/translations/pcsx2-qt_da-DK.qm
%lang(de) %{_datadir}/PCSX2/translations/pcsx2-qt_de-DE.qm
%lang(el) %{_datadir}/PCSX2/translations/pcsx2-qt_el-GR.qm
%lang(en) %{_datadir}/PCSX2/translations/pcsx2-qt_en-fg.qm
%lang(en) %{_datadir}/PCSX2/translations/pcsx2-qt_en-US.qm
%lang(es) %{_datadir}/PCSX2/translations/pcsx2-qt_es-419.qm
%lang(es) %{_datadir}/PCSX2/translations/pcsx2-qt_es-ES.qm
%lang(fa) %{_datadir}/PCSX2/translations/pcsx2-qt_fa-IR.qm
%lang(fi) %{_datadir}/PCSX2/translations/pcsx2-qt_fi-FI.qm
%lang(fr) %{_datadir}/PCSX2/translations/pcsx2-qt_fr-FR.qm
%lang(gn) %{_datadir}/PCSX2/translations/pcsx2-qt_gn-PY.qm
%lang(he) %{_datadir}/PCSX2/translations/pcsx2-qt_he-IL.qm
%lang(hi) %{_datadir}/PCSX2/translations/pcsx2-qt_hi-IN.qm
%lang(hr) %{_datadir}/PCSX2/translations/pcsx2-qt_hr-HR.qm
%lang(hu) %{_datadir}/PCSX2/translations/pcsx2-qt_hu-HU.qm
%lang(id) %{_datadir}/PCSX2/translations/pcsx2-qt_id-ID.qm
%lang(it) %{_datadir}/PCSX2/translations/pcsx2-qt_it-IT.qm
%lang(ja) %{_datadir}/PCSX2/translations/pcsx2-qt_ja-JP.qm
%lang(ka) %{_datadir}/PCSX2/translations/pcsx2-qt_ka-GE.qm
%lang(ko) %{_datadir}/PCSX2/translations/pcsx2-qt_ko-KR.qm
%lang(lt) %{_datadir}/PCSX2/translations/pcsx2-qt_lt-LT.qm
%lang(lv) %{_datadir}/PCSX2/translations/pcsx2-qt_lv-LV.qm
%lang(nl) %{_datadir}/PCSX2/translations/pcsx2-qt_nl-NL.qm
%lang(no) %{_datadir}/PCSX2/translations/pcsx2-qt_no-NO.qm
%lang(pl) %{_datadir}/PCSX2/translations/pcsx2-qt_pl-PL.qm
%lang(pt_BR) %{_datadir}/PCSX2/translations/pcsx2-qt_pt-BR.qm
%lang(pt) %{_datadir}/PCSX2/translations/pcsx2-qt_pt-PT.qm
%lang(qu) %{_datadir}/PCSX2/translations/pcsx2-qt_qu-PE.qm
%lang(ro) %{_datadir}/PCSX2/translations/pcsx2-qt_ro-RO.qm
%lang(ru) %{_datadir}/PCSX2/translations/pcsx2-qt_ru-RU.qm
%lang(sr) %{_datadir}/PCSX2/translations/pcsx2-qt_sr-SP.qm
%lang(sv) %{_datadir}/PCSX2/translations/pcsx2-qt_sv-SE.qm
%lang(tr) %{_datadir}/PCSX2/translations/pcsx2-qt_tr-TR.qm
%lang(uk) %{_datadir}/PCSX2/translations/pcsx2-qt_uk-UA.qm
%lang(vi) %{_datadir}/PCSX2/translations/pcsx2-qt_vi-VN.qm
%lang(zh_CN) %{_datadir}/PCSX2/translations/pcsx2-qt_zh-CN.qm
%lang(zh_TW) %{_datadir}/PCSX2/translations/pcsx2-qt_zh-TW.qm
