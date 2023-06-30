# TODO: use system ca-certificates
# - libdispatch
#
# Conditional build:
%bcond_without	doc     # don't generate documentation (bootstrap build w/o gnustep-base)
#
# gc is used for gnugc-*-* libcombo
%if "%(gnustep-config --variable=LIBRARY_COMBO | cut -d- -f1)" == "gnugc"
%define	with_gc	1
%endif
Summary:	GNUstep Base library package
Summary(pl.UTF-8):	Podstawowa biblioteka GNUstep
Name:		gnustep-base
%define	ver	1.24
Version:	%{ver}.6
Release:	21
License:	LGPL v2+ (library), GPL v3+ (applications)
Group:		Libraries
Source0:	ftp://ftp.gnustep.org/pub/gnustep/core/%{name}-%{version}.tar.gz
# Source0-md5:	02e45ae9a7e5e75bf32cc1a6e8381bc1
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-pass-arguments.patch
Patch1:		%{name}-ac.patch
Patch2:		%{name}-link.patch
Patch3:		%{name}-icu68.patch
URL:		http://www.gnustep.org/
BuildRequires:	autoconf >= 2.60
BuildRequires:	avahi-devel
%{?with_doc:BuildRequires:	docbook-dtd41-sgml}
%{?with_gc:BuildRequires:	gc-devel}
BuildRequires:	gcc-objc
BuildRequires:	gmp-devel
BuildRequires:	gnustep-make-devel >= 1.13.1
BuildRequires:	gnutls-devel >= 1.4.0
BuildRequires:	libffi-devel >= 3.0.9
BuildRequires:	libgcrypt-devel
BuildRequires:	libicu-devel >= 4.0
BuildRequires:	libxml2-devel >= 2.3.0
BuildRequires:	libxslt-devel >= 1.1.21
BuildRequires:	pkgconfig
%{?with_doc:BuildRequires:	texinfo-texi2dvi}
BuildRequires:	zlib-devel
Requires(post):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires:	glibc >= 6:2.3.5-7.6
Requires:	gnustep-make >= 1.13.1
Requires:	sed >= 4.0
# with gdomap in /etc/services
Requires:	setup >= 2.4.3
Conflicts:	gnustep-core
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# libgnustep-base refers to some non-function ffi_* symbols
%define		skip_post_check_so	libgnustep-base.so.*

%description
The GNUstep Base Library is a library of general-purpose,
non-graphical Objective C objects. For example, it includes classes
for strings, object collections, byte streams, typed coders,
invocations, notifications, notification dispatchers, moments in time,
network ports, remote object messaging support (distributed objects),
event loops, and random number generators.

%description -l pl.UTF-8
Podstawowa biblioteka GNUstep jest biblioteką innych niż graficzne
obiektów ogólnego przeznaczenia dla Objective C. Zawiera np. klasy dla
stringów, kolekcji, strumieni, koderów typów, powiadamiania, portów
sieci, obiektów rozproszonych, pętli zdarzeń, generatorów liczb
losowych.

%package devel
Summary:	GNUstep Base headers
Summary(pl.UTF-8):	Pliki nagłówkowe podstawowej biblioteki GNUstep
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	gcc-objc
Requires:	gmp-devel
Requires:	gnustep-make-devel >= 1.13.1
Requires:	libffi-devel >= 3.0.9
Requires:	libxml2-devel
Requires:	zlib-devel

%description devel
Header files required to build applications against the GNUstep Base
library.

%description devel -l pl.UTF-8
Pliki nagłówkowe potrzebne do budowania aplikacji używających
podstawowej biblioteki GNUstep.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__autoconf} -Iconfig

# don't assume that GNUstep.sh is imported in environment
export GNUSTEP_MAKEFILES=%{_datadir}/GNUstep/Makefiles
export GNUSTEP_FLATTENED=yes

# gnustep can use one of 3 ways of getting argc,argv,env:
# - /proc (default on Linux) - gnustep programs won't run in procless system
# - fake-main hack (main is secretly renamed and wrapped)
# - pass-arguments (program must call NSProcessInfo initialize)
GNUSTEP_INSTALLATION_DOMAIN=SYSTEM \
%configure \
	--disable-ffcall \
	--enable-libffi \
	--enable-pass-arguments \
	--with-zeroconf=avahi

# fake GUI_MAKE_LOADED to avoid linking with gnustep-gui
%{__make} -j1 \
	GNUSTEP_INSTALLATION_DOMAIN=SYSTEM \
	GUI_MAKE_LOADED=yes \
	GNUSTEP_MAKEFILES=`gnustep-config --variable=GNUSTEP_MAKEFILES` \
	messages=yes

%if %{with doc}
# needs already built gnustep-base
export LD_LIBRARY_PATH=`pwd`/Source/obj
# build seems racy, use -j1
%{__make} -j1 -C Documentation \
	GNUSTEP_INSTALLATION_DOMAIN=SYSTEM \
	GNUSTEP_MAKEFILES=`gnustep-config --variable=GNUSTEP_MAKEFILES`
%{__make} -j1 -C Documentation/manual \
	GNUSTEP_INSTALLATION_DOMAIN=SYSTEM \
	GNUSTEP_MAKEFILES=`gnustep-config --variable=GNUSTEP_MAKEFILES`
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/etc/sysconfig}

export GNUSTEP_MAKEFILES=%{_datadir}/GNUstep/Makefiles
export GNUSTEP_FLATTENED=yes

%{__make} -j1 install \
	GNUSTEP_INSTALLATION_DOMAIN=SYSTEM \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/gnustep
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/gnustep

echo 'GMT' > $RPM_BUILD_ROOT%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/localtime

%if %{with doc}
%{__make} -j1 -C Documentation install \
	GNUSTEP_INSTALLATION_DOMAIN=SYSTEM \
	DESTDIR=$RPM_BUILD_ROOT

%{__make} -j1 -C Documentation/manual install \
	GNUSTEP_INSTALLATION_DOMAIN=SYSTEM \
	DESTDIR=$RPM_BUILD_ROOT

%{__mv} $RPM_BUILD_ROOT%{_infodir}/{manual,gnustep-base-manual}.info

# not (yet?) supported by rpm-compress-doc
find $RPM_BUILD_ROOT%{_datadir}/GNUstep/Documentation \
	-type f -a ! -name '*.html' -a ! -name '*.gz' -a ! -name '*.jpg' -a ! -name '*.css' | xargs gzip -9nf
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/chkconfig --add gnustep
if [ -f /var/lock/subsys/gnustep ]; then
	/etc/rc.d/init.d/gnustep restart 1>&2
else
	echo "Run \"/etc/rc.d/init.d/gnustep start\" to start gnustep services."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/gnustep ]; then
		/etc/rc.d/init.d/gnustep stop 1>&2
	fi
	/sbin/chkconfig --del gnustep
fi

%postun -p /sbin/ldconfig

%triggerpostun -- %{name} < 1.11.0-1.1
sed -i -e "/^%(echo %{_prefix}/Libraries/ | sed -e 's,/,\\/,g')$/d" /etc/ld.so.conf

%files
%defattr(644,root,root,755)
%doc ChangeLog*

%attr(755,root,root) %{_bindir}/HTMLLinker
%attr(755,root,root) %{_bindir}/autogsdoc
%attr(755,root,root) %{_bindir}/cvtenc
%attr(755,root,root) %{_bindir}/defaults
%attr(755,root,root) %{_bindir}/gdnc
%attr(755,root,root) %{_bindir}/gdomap
%attr(755,root,root) %{_bindir}/gspath
%attr(755,root,root) %{_bindir}/make_strings
%attr(755,root,root) %{_bindir}/pl
%attr(755,root,root) %{_bindir}/pl2link
%attr(755,root,root) %{_bindir}/pldes
%attr(755,root,root) %{_bindir}/plget
%attr(755,root,root) %{_bindir}/plmerge
%attr(755,root,root) %{_bindir}/plparse
%attr(755,root,root) %{_bindir}/plser
%attr(755,root,root) %{_bindir}/sfparse
%attr(755,root,root) %{_bindir}/xmlparse
# is suid necessary here??? it runs as daemon...
#%attr(4755,root,root) %{_bindir}/gdomap

%attr(755,root,root) %{_libdir}/libgnustep-base.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgnustep-base.so.%{ver}

%{_mandir}/man1/autogsdoc.1*
%{_mandir}/man1/cvtenc.1*
%{_mandir}/man1/defaults.1*
%{_mandir}/man1/gdnc.1*
%{_mandir}/man1/gspath.1*
%{_mandir}/man1/pldes.1*
%{_mandir}/man1/sfparse.1*
%{_mandir}/man1/xmlparse.1*
%{_mandir}/man8/gdomap.8*

%attr(754,root,root) /etc/rc.d/init.d/gnustep
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/gnustep

%dir %{_libdir}/GNUstep/DTDs
%{_libdir}/GNUstep/DTDs/*.dtd
%{_libdir}/GNUstep/DTDs/*.rnc

%dir %{_libdir}/GNUstep/Libraries
%dir %{_libdir}/GNUstep/Libraries/gnustep-base
%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions
%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}
%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources
%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/GSTLS
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/GSTLS/ca-certificates.crt
%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages
%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones

%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/*.plist
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/English.lproj
%lang(eo) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Esperanto.lproj
%lang(fr) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/French.lproj
%lang(de) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/German.lproj
%lang(it) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Italian.lproj
%lang(ko) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Korean.lproj
%lang(es) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Spanish.lproj
%lang(zh_TW) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/TraditionalChinese.lproj
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Locale.*
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/English
%lang(nl) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Dutch
%lang(eo) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Esperanto
%lang(fr) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/French
%lang(de) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/German
%lang(hu) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Hungarian
%lang(it) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Italian
%lang(ko) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Korean
%lang(ru) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Russian
%lang(sk) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Slovak
%lang(es) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Spanish
%lang(zh_TW) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/TraditionalChinese
%lang(uk) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/Languages/Ukrainian

%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/GNUmakefile
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/GNUstep_zones
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/README
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/abbreviations
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/regions
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/zones
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/*.m
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/*.plist
# FIXME: FHS
%config(noreplace) %verify(not md5 mtime size) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/localtime

%if %{with doc}
%docdir %{_datadir}/GNUstep/Documentation
%{_datadir}/GNUstep/Documentation/*.jpg
%{_datadir}/GNUstep/Documentation/index.html
%{_datadir}/GNUstep/Documentation/style.css
%dir %{_datadir}/GNUstep/Documentation/Developer/Base
%{_datadir}/GNUstep/Documentation/Developer/Base/ReleaseNotes
%endif

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libgnustep-base.so
%{_includedir}/Foundation
%{_includedir}/GNUstepBase
%{_includedir}/gnustep

%if %{with doc}
%docdir %{_datadir}/GNUstep/Documentation
%{_datadir}/GNUstep/Documentation/Developer/Base/General
%{_datadir}/GNUstep/Documentation/Developer/Base/ProgrammingManual
%{_datadir}/GNUstep/Documentation/Developer/Base/Reference
%{_datadir}/GNUstep/Documentation/Developer/BaseAdditions
%{_datadir}/GNUstep/Documentation/Developer/CodingStandards
%{_datadir}/GNUstep/Documentation/Developer/Tools
%{_infodir}/gnustep-base-manual.info*
%endif

%dir %{_datadir}/GNUstep/Makefiles/Additional
%{_datadir}/GNUstep/Makefiles/Additional/base.make
