Summary:	GNUstep Base library package
Summary(pl):	Podstawowa biblioteka GNUstep
Name:		gnustep-base
Version:	1.5.1
Release:	0.1
License:	GPL
Vendor:		The Seawood Project
Group:		Development/Tools
Source0:	ftp://ftp.gnustep.org/pub/gnustep/core/%{name}-%{version}.tar.gz
Patch0:		%{name}-link.patch
URL:		http://www.gnustep.org/
BuildRequires:	ffcall-devel
BuildRequires:	gcc-objc
BuildRequires:	gmp-devel
BuildRequires:	gnustep-make-devel >= 1.5.1
BuildRequires:	libxml2 >= 2.3.0
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
Requires(post,preun):	grep
Requires(post,preun):	/sbin/chkconfig
Requires(post,postun):	/sbin/ldconfig
Requires:	gnustep-make
Conflicts:	gnustep-core
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define         _prefix         /usr/lib/GNUstep

%define		libcombo	gnu-gnu-gnu
%define		gsos		linux-gnu
%ifarch %{ix86}
%define		gscpu		ix86
%else
# also s/alpha.*/alpha/, but we use only "alpha" arch for now
%define		gscpu		%{_target_cpu}
%endif

%description
The GNUstep Base Library is a library of general-purpose,
non-graphical Objective C objects. For example, it includes classes
for strings, object collections, byte streams, typed coders,
invocations, notifications, notification dispatchers, moments in time,
network ports, remote object messaging support (distributed objects),
event loops, and random number generators.

%description -l pl
Podstawowa biblioteka GNUstep jest bibliotek± innych ni¿ graficzne
obiektów ogólnego przeznaczenia dla Objective C. Zawiera np. klasy dla
stringów, kolekcji, strumieni, koderów typów, powiadamiania, portów
sieci, obiektów rozproszonych, pêtli zdarzeñ, generatorów liczb
losowych.

%package devel
Summary:	GNUstep Base headers
Summary(pl):	Pliki nag³ówkowe podstawowej biblioteki GNUstep
Group:		Development/Libraries
Requires:	%{name} = %{version}
Requires:	gnustep-make-devel
Conflicts:	gnustep-core

%description devel
Header files required to build applications against the GNUstep Base
library.

%description devel -l pl
Pliki nag³ówkowe potrzebne do budowania aplikacji u¿ywaj±cych
podstawowej biblioteki GNUstep.

%prep
%setup -q
%patch -p1

%build
. %{_prefix}/System/Makefiles/GNUstep.sh
%configure

%{__make}

# requires already installed gnustep-base
#%{__make} -C Documentation

%install
rm -rf $RPM_BUILD_ROOT
. %{_prefix}/System/Makefiles/GNUstep.sh
%{__make} install \
	INSTALL_ROOT_DIR=$RPM_BUILD_ROOT \
	GNUSTEP_INSTALLATION_DIR=$RPM_BUILD_ROOT%{_prefix}/System

#%{__make} -C Documentation install \
#	GNUSTEP_INSTALLATION_DIR=$RPM_BUILD_ROOT%{_prefix}/System

install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
cat > $RPM_BUILD_ROOT/etc/rc.d/init.d/gnustep << EOF
#!/bin/sh
#
# gnustep daemons
#
# chkconfig: 2345 35 65
# description: Starts gnustep daemons
#
# Source function library.
. /etc/rc.d/init.d/functions

case "\$1" in
  start)
	if [ ! -f /var/lock/subsys/gnustep ]; then
		msg_starting "gnustep services"
		daemon %{_prefix}/Tools/%{gscpu}/%{gsos}/gdomap
		RETVAL=$?
		[ $RETVAL -eq 0 ] && touch /var/lock/subsys/gnustep
	else
		msg_already_running "gnustep services"
		exit 1
	fi
	;;
  stop)
	if [ -f /var/lock/subsys/gnustep ]; then
		msg_stopping "gnustep services"
		killproc gdomap
		RETVAL=$?
		rm -f /var/lock/subsys/gnustep
	else
		msg_not_running "gnustep services"
		exit 1
	fi
	;;
   status)
	status gdomap
	RETVAL=$?
        ;;
   restart|reload)
	\$0 stop
	\$0 start
	;;
    *)
        msg_usage "$0 {start|stop|status|restart|reload}"
        exit 1
esac

exit $RETVAL
EOF

echo 'GMT' > $RPM_BUILD_ROOT%{_prefix}/System/Libraries/Resources/NSTimeZones/localtime

# not (yet?) supported by rpm-compress-doc
find $RPM_BUILD_ROOT%{_prefix}/System/Documentation/Developer -type f | xargs gzip -9nf

%clean
rm -rf $RPM_BUILD_ROOT

%post
umask 022
if ! grep -q '^gdomap' /etc/services ; then
	echo "gdomap 538/tcp # GNUstep distrib objects" >> /etc/services
	echo "gdomap 538/udp # GNUstep distrib objects" >> /etc/services
fi
if ! grep -q '%{_prefix}/Libraries/%{gscpu}/%{gsos}/%{libcombo}' \
    /etc/ld.so.conf ; then
	echo "%{_prefix}/Libraries/%{gscpu}/%{gsos}/%{libcombo}" >> /etc/ld.so.conf
fi
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

%postun
if [ "$1" = "0" ]; then
	grep -v "^%{_prefix}/Libraries/%{gscpu}/%{gsos}/%{libcombo}$" /etc/ld.so.conf \
		> /etc/ld.so.conf.tmp
	mv -f /etc/ld.so.conf.tmp /etc/ld.so.conf
	/sbin/ldconfig
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog* NEWS README
%attr(754,root,root) /etc/rc.d/init.d/gnustep

%{_prefix}/System/Libraries/Resources/DocTemplates
%{_prefix}/System/Libraries/Resources/DTDs
%{_prefix}/System/Libraries/Resources/NSCharacterSets
%dir %{_prefix}/System/Libraries/Resources/NSTimeZones
%{_prefix}/System/Libraries/Resources/NSTimeZones/GNUmakefile
%{_prefix}/System/Libraries/Resources/NSTimeZones/GNUstep_zones
%{_prefix}/System/Libraries/Resources/NSTimeZones/README
%{_prefix}/System/Libraries/Resources/NSTimeZones/abbreviations
%{_prefix}/System/Libraries/Resources/NSTimeZones/regions
%{_prefix}/System/Libraries/Resources/NSTimeZones/zones
%{_prefix}/System/Libraries/Resources/NSTimeZones/*.m
%config(noreplace) %verify(not size mtime md5) %{_prefix}/System/Libraries/Resources/NSTimeZones/localtime
%{_prefix}/System/Libraries/Resources/English.lproj
%lang(fr) %{_prefix}/System/Libraries/Resources/French.lproj
%lang(de) %{_prefix}/System/Libraries/Resources/German.lproj
%lang(it) %{_prefix}/System/Libraries/Resources/Italian.lproj
%dir %{_prefix}/System/Libraries/Resources/Languages
%{_prefix}/System/Libraries/Resources/Languages/Locale.*
%lang(nl) %{_prefix}/System/Libraries/Resources/Languages/Dutch
%{_prefix}/System/Libraries/Resources/Languages/English
%lang(fr) %{_prefix}/System/Libraries/Resources/Languages/French
%lang(de) %{_prefix}/System/Libraries/Resources/Languages/German
%lang(it) %{_prefix}/System/Libraries/Resources/Languages/Italian
%lang(ru) %{_prefix}/System/Libraries/Resources/Languages/Russian
%lang(sk) %{_prefix}/System/Libraries/Resources/Languages/Slovak
%lang(uk) %{_prefix}/System/Libraries/Resources/Languages/UkraineRussian

%dir %{_prefix}/System/Libraries/%{gscpu}
%dir %{_prefix}/System/Libraries/%{gscpu}/%{gsos}
%dir %{_prefix}/System/Libraries/%{gscpu}/%{gsos}/%{libcombo}
%attr(755,root,root) %{_prefix}/System/Libraries/%{gscpu}/%{gsos}/%{libcombo}/lib*.so.*

%dir %{_prefix}/System/Library/Bundles/SSL.bundle
%{_prefix}/System/Library/Bundles/SSL.bundle/Resources
%dir %{_prefix}/System/Library/Bundles/SSL.bundle/%{gscpu}
%dir %{_prefix}/System/Library/Bundles/SSL.bundle/%{gscpu}/%{gsos}
%dir %{_prefix}/System/Library/Bundles/SSL.bundle/%{gscpu}/%{gsos}/%{libcombo}
%attr(755,root,root) %{_prefix}/System/Library/Bundles/SSL.bundle/%{gscpu}/%{gsos}/%{libcombo}/SSL

%dir %{_prefix}/System/Tools/%{gscpu}
%dir %{_prefix}/System/Tools/%{gscpu}/%{gsos}
# is suid necessary here??? it runs as daemon...
#%attr(4755,root,root) %{_prefix}/System/Tools/%{gscpu}/%{gsos}/gdomap
%attr(755,root,root) %{_prefix}/System/Tools/%{gscpu}/%{gsos}/gdomap
%dir %{_prefix}/System/Tools/%{gscpu}/%{gsos}/%{libcombo}
%attr(755,root,root) %{_prefix}/System/Tools/%{gscpu}/%{gsos}/%{libcombo}/*

%files devel
%defattr(644,root,root,755)
%{_prefix}/System/Headers/Foundation
%{_prefix}/System/Headers/gnustep
%{_prefix}/System/Headers/%{gscpu}
%{_prefix}/System/Libraries/%{gscpu}/%{gsos}/%{libcombo}/lib*.so
%dir %{_prefix}/System/Makefiles/Additional
%{_prefix}/System/Makefiles/Additional/*.make
