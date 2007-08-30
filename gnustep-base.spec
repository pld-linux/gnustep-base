#
# Conditional build:
%bcond_without	doc	# don't generate documentation (bootstrap build w/o gnustep-base)
#
Summary:	GNUstep Base library package
Summary(pl.UTF-8):	Podstawowa biblioteka GNUstep
Name:		gnustep-base
Version:	1.14.0
Release:	0.1
License:	LGPL/GPL
Group:		Libraries
Source0:	ftp://ftp.gnustep.org/pub/gnustep/core/%{name}-%{version}.tar.gz
# Source0-md5:	10a24a5568c5505c4b7480f170733d4d
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Patch0:		%{name}-pass-arguments.patch
URL:		http://www.gnustep.org/
%{?with_doc:BuildRequires:	docbook-dtd41-sgml}
BuildRequires:	ffcall-devel
BuildRequires:	gcc-objc
BuildRequires:	gmp-devel
%{?with_doc:BuildRequires:	gnustep-base-devel >= 1.8.0}
BuildRequires:	gnustep-make-devel >= 1.11.2
BuildRequires:	libxml2-devel >= 2.3.0
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

%define         _prefix         /usr/%{_lib}/GNUstep

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
export GNUSTEP_MAKEFILES=%{_prefix}/System/Library/Makefiles
export GNUSTEP_FLATTENED=yes

# gnustep can use one of 3 ways of getting argc,argv,env:
# - /proc (default on Linux) - gnustep programs won't run in procless system
# - fake-main hack (main is secretly renamed and wrapped)
# - pass-arguments (program must call NSProcessInfo initialize)
%configure \
	--enable-pass-arguments

# fake GUI_MAKE_LOADED to avoid linking with gnustep-gui
%{__make} \
	GUI_MAKE_LOADED=yes \
	messages=yes

%if %{with doc}
export LD_LIBRARY_PATH=`pwd`/Source/obj
# requires already installed gnustep-base
%{__make} -C Documentation
%{__make} -C Documentation/manual
%endif

%install
rm -rf $RPM_BUILD_ROOT
export GNUSTEP_MAKEFILES=%{_prefix}/System/Library/Makefiles
export GNUSTEP_FLATTENED=yes

%{__make} install \
	INSTALL_ROOT_DIR=$RPM_BUILD_ROOT \
	GNUSTEP_INSTALLATION_DIR=$RPM_BUILD_ROOT%{_prefix}/System

%if %{with doc}
%{__make} -C Documentation install \
	GNUSTEP_INSTALLATION_DIR=$RPM_BUILD_ROOT%{_prefix}/System
%{__make} -C Documentation/manual install \
	GNUSTEP_INSTALLATION_DIR=$RPM_BUILD_ROOT%{_prefix}/System
# not (yet?) supported by rpm-compress-doc
find $RPM_BUILD_ROOT%{_prefix}/System/Library/Documentation \
	-type f -a ! -name '*.html' -a ! -name '*.gz' -a ! -name '*.jpg' -a ! -name '*.css' | xargs gzip -9nf
%endif

install -d $RPM_BUILD_ROOT%{_initrddir}
sed -e "s!@TOOLSARCHDIR@!%{_prefix}/System/Tools/!" %{SOURCE1} \
	> $RPM_BUILD_ROOT%{_initrddir}/gnustep

install -d $RPM_BUILD_ROOT/etc/sysconfig
install %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/gnustep

echo 'GMT' > $RPM_BUILD_ROOT%{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/localtime

install -d $RPM_BUILD_ROOT/etc/ld.so.conf.d
echo '%{_prefix}/System/Library/Libraries' > $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{name}.conf

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
/etc/ld.so.conf.d/%{name}.conf
%attr(754,root,root) %{_initrddir}/gnustep
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/gnustep

%dir %{_prefix}/System/Library/Bundles/SSL.bundle
%attr(755,root,root) %{_prefix}/System/Library/Bundles/SSL.bundle/SSL
%{_prefix}/System/Library/Bundles/SSL.bundle/Resources

%docdir %{_prefix}/System/Library/Documentation
%if %{with doc}
%{_prefix}/System/Library/Documentation/*.jpg
%{_prefix}/System/Library/Documentation/index.html
%{_prefix}/System/Library/Documentation/style.css
%dir %{_prefix}/System/Library/Documentation/Developer/Base
%{_prefix}/System/Library/Documentation/Developer/Base/ReleaseNotes
%endif
%dir %{_prefix}/System/Library/Documentation/man/man8
%{_prefix}/System/Library/Documentation/man/man1/*.1*
%{_prefix}/System/Library/Documentation/man/man8/*.8*

%dir %{_prefix}/System/Library/DTDs
%{_prefix}/System/Library/DTDs/*.dtd
%{_prefix}/System/Library/DTDs/*.rnc

%dir %{_prefix}/System/Library/Libraries/Resources/gnustep-base
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/*.plist
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/English.lproj
%lang(eo) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Esperanto.lproj
%lang(fr) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/French.lproj
%lang(de) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/German.lproj
%lang(it) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Italian.lproj
%lang(ko) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Korean.lproj
%lang(es) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Spanish.lproj
%lang(zh_TW) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/TraditionalChinese.lproj
%dir %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Locale.*
%lang(nl) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Dutch
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/English
%lang(eo) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Esperanto
%lang(fr) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/French
%lang(de) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/German
%lang(hu) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Hungarian
%lang(it) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Italian
%lang(ko) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Korean
%lang(ru) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Russian
%lang(sk) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Slovak
%lang(es) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Spanish
%lang(zh_TW) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/TraditionalChinese
%lang(uk) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/Languages/Ukrainian
%dir %{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/GNUmakefile
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/GNUstep_zones
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/README
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/abbreviations
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/regions
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/zones
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/*.m
%{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/*.plist
%config(noreplace) %verify(not md5 mtime size) %{_prefix}/System/Library/Libraries/Resources/gnustep-base/NSTimeZones/localtime

%attr(755,root,root) %{_prefix}/System/Library/Libraries/libgnustep-base.so.*

# is suid necessary here??? it runs as daemon...
#%attr(4755,root,root) %{_prefix}/System/Tools/gdomap
%dir %{_prefix}/System/Tools
%attr(755,root,root) %{_prefix}/System/Tools/*

%files devel
%defattr(644,root,root,755)
%if %{with doc}
%docdir %{_prefix}/System/Library/Documentation
%{_prefix}/System/Library/Documentation/Developer/Base/General
%{_prefix}/System/Library/Documentation/Developer/Base/ProgrammingManual
%{_prefix}/System/Library/Documentation/Developer/Base/Reference
%{_prefix}/System/Library/Documentation/Developer/BaseAdditions
%{_prefix}/System/Library/Documentation/Developer/CodingStandards
%{_prefix}/System/Library/Documentation/Developer/Tools
%{_prefix}/System/Library/Documentation/info/*.info*
%endif

%{_prefix}/System/Library/Headers/Foundation
%{_prefix}/System/Library/Headers/GNUstepBase
%{_prefix}/System/Library/Headers/gnustep
%{_prefix}/System/Library/Headers/*.h

%attr(755,root,root) %{_prefix}/System/Library/Libraries/libgnustep-base.so
%dir %{_prefix}/System/Library/Makefiles/Additional
%{_prefix}/System/Library/Makefiles/Additional/base.make
