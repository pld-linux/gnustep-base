# Conditional build:
%bcond_without doc     # don't generate documentation (bootstrap build w/o gnustep-base)
#
%define		 ver 1.15
Summary:	GNUstep Base library package
Summary(pl.UTF-8):	Podstawowa biblioteka GNUstep
Name:		gnustep-base
Version:	%{ver}.3
Release:	4
License:	LGPL/GPL
Group:		Libraries
Source0:	ftp://ftp.gnustep.org/pub/gnustep/core/%{name}-%{version}.tar.gz
# Source0-md5:	67449dd0d8c4ef096fde46bf65503982
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-pass-arguments.patch
URL:		http://www.gnustep.org/
%{?with_doc:BuildRequires:	docbook-dtd41-sgml}
BuildRequires:	gcc-objc
BuildRequires:	gmp-devel
BuildRequires:	gnustep-make-devel >= 1.11.2
BuildRequires:	libffi-devel
BuildRequires:	libxml2-devel >= 2.3.0
BuildRequires:	libxslt-devel >= 1.1.21
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	zlib-devel
Requires(post):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires(triggerpostun):	sed >= 4.0
Requires:	glibc >= 6:2.3.5-7.6
Requires:	gnustep-make >= 1.11.2
# with gdomap in /etc/services
Requires:	setup >= 2.4.3
Conflicts:	gnustep-core
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
Requires:	ffcall-devel
Requires:	gcc-objc
Requires:	gmp-devel
Requires:	gnustep-make-devel >= 1.11.2
Requires:	libxml2-devel
Requires:	zlib-devel
Conflicts:	gnustep-core

%description devel
Header files required to build applications against the GNUstep Base
library.

%description devel -l pl.UTF-8
Pliki nagłówkowe potrzebne do budowania aplikacji używających
podstawowej biblioteki GNUstep.

%prep
%setup -q
%patch0 -p1

%build
# don't assume that GNUstep.sh is imported in environment
export GNUSTEP_MAKEFILES=%{_datadir}/GNUstep/Makefiles
export GNUSTEP_FLATTENED=yes

# gnustep can use one of 3 ways of getting argc,argv,env:
# - /proc (default on Linux) - gnustep programs won't run in procless system
# - fake-main hack (main is secretly renamed and wrapped)
# - pass-arguments (program must call NSProcessInfo initialize)
%configure \
	--enable-pass-arguments \
	--enable-libffi \
	--disable-ffcall

# fake GUI_MAKE_LOADED to avoid linking with gnustep-gui
%{__make} \
	GUI_MAKE_LOADED=yes \
	GNUSTEP_MAKEFILES=`gnustep-config --variable=GNUSTEP_MAKEFILES` \
	messages=yes

%if %{with doc}
export LD_LIBRARY_PATH=`pwd`/Source/obj
# with __make -j2:
# 	mkdir: cannot create directory `../Documentation/BaseTools': File exists
#	make[1]: *** [../Documentation/BaseTools] Error 1
#	make[1]: *** Waiting for unfinished jobs....
# requires already installed gnustep-base
%{__make} -j1 -C Documentation \
	GNUSTEP_MAKEFILES=`gnustep-config --variable=GNUSTEP_MAKEFILES`
%{__make} -C Documentation/manual \
	GNUSTEP_MAKEFILES=`gnustep-config --variable=GNUSTEP_MAKEFILES`
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_initrddir},/etc/sysconfig}

export GNUSTEP_MAKEFILES=%{_datadir}/GNUstep/Makefiles
export GNUSTEP_FLATTENED=yes

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT%{_initrddir}/gnustep
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/gnustep

echo 'GMT' > $RPM_BUILD_ROOT%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/localtime

# Fix .so symlink
(cd $RPM_BUILD_ROOT%{_libdir} ; ln -sf libgnustep-base.so.*.*.* libgnustep-base.so)

%if %{with doc}
%{__make} -C Documentation install \
	DESTDIR=$RPM_BUILD_ROOT

%{__make} -C Documentation/manual install \
	DESTDIR=$RPM_BUILD_ROOT

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
%if %{with doc}
%docdir %{_datadir}/GNUstep/Documentation
%{_datadir}/GNUstep/Documentation/*.jpg
%{_datadir}/GNUstep/Documentation/index.html
%{_datadir}/GNUstep/Documentation/style.css
%dir %{_datadir}/GNUstep/Documentation
%dir %{_datadir}/GNUstep/Documentation/Developer
%dir %{_datadir}/GNUstep/Documentation/Developer/Base
%{_datadir}/GNUstep/Documentation/Developer/Base/ReleaseNotes
%endif

%attr(754,root,root) %{_initrddir}/gnustep
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/gnustep

%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/SSL.bundle
%attr(755,root,root) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/SSL.bundle/SSL
%{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/SSL.bundle/Resources

%dir %{_libdir}/GNUstep/DTDs
%{_libdir}/GNUstep/DTDs/*.dtd
%{_libdir}/GNUstep/DTDs/*.rnc

%dir %{_libdir}/GNUstep/Libraries
%dir %{_libdir}/GNUstep/Libraries/gnustep-base
%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions
%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}
%dir %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources
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
%config(noreplace) %verify(not md5 mtime size) %{_libdir}/GNUstep/Libraries/gnustep-base/Versions/%{ver}/Resources/NSTimeZones/localtime

%attr(755,root,root) %{_libdir}/libgnustep-base.so.*.*.*

# is suid necessary here??? it runs as daemon...
#%attr(4755,root,root) %{_bindir}/gdomap
%attr(755,root,root) %{_bindir}/*

%{_mandir}/man1/*.1*
%{_mandir}/man8/*.8*

%files devel
%defattr(644,root,root,755)
%dir %{_datadir}/GNUstep/Makefiles/Additional
%{_datadir}/GNUstep/Makefiles/Additional/base.make
%if %{with doc}
%docdir %{_datadir}/GNUstep/Documentation
%{_datadir}/GNUstep/Documentation/Developer/Base/General
%{_datadir}/GNUstep/Documentation/Developer/Base/ProgrammingManual
%{_datadir}/GNUstep/Documentation/Developer/Base/Reference
%{_datadir}/GNUstep/Documentation/Developer/BaseAdditions
%{_datadir}/GNUstep/Documentation/Developer/CodingStandards
%{_datadir}/GNUstep/Documentation/Developer/Tools
%{_infodir}/*.info*
%endif

%{_includedir}/Foundation
%{_includedir}/GNUstepBase
%{_includedir}/gnustep

%attr(755,root,root) %{_libdir}/libgnustep-base.so

%dir %{_datadir}/GNUstep/Makefiles/Additional
%{_datadir}/GNUstep/Makefiles/Additional/base.make
