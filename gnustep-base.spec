Summary:	GNUstep Base library package
Summary(pl):	Podstawowa biblioteka GNUstep
Name:		gnustep-base
Version:	1.0.2
Release:	1
License:	GPL
Vendor:		The Seawood Project
Group:		Development/Tools
Source0:	ftp://ftp.gnustep.org/pub/gnustep/core/%{name}-%{version}.tar.gz
URL:		http://www.gnustep.org/
BuildRequires:	gnustep-make-devel
BuildRequires:	libxml2 >= 2.2.3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Conflicts:	gnustep-core
Requires:	gnustep-make
Prereq:		/sbin/chkconfig

%description
The GNUstep Base Library is a library of general-purpose,
non-graphical Objective C objects. For example, it includes classes
for strings, object collections, byte streams, typed coders,
invocations, notifications, notification dispatchers, moments in time,
network ports, remote object messaging support (distributed objects),
event loops, and random number generators. Library combo is
%{libcombo}. %{_buildblurb}

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
Requires:	%{name} = %{version}, gnustep-make-devel
Conflicts:	gnustep-core

%description devel
Header files required to build applications against the GNUstep Base
library. Library combo is %{libcombo}. %{_buildblurb}

%description devel -l pl
Pliki nag³ówkowe potrzebne do budowania aplikacji u¿ywaj±cych
podstawowej biblioteki GNUstep.

%prep
%setup -q

%build
if [ -z "$GNUSTEP_SYSTEM_ROOT" ]; then
   . %{_prefix}/GNUstep/System/Makefiles/GNUstep.sh
fi
CFLAGS="%{rpmcflags}" ./configure --prefix=%{_prefix}/GNUstep
# --with-library-combo=%{libcombo}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
if [ -z "$GNUSTEP_SYSTEM_ROOT" ]; then
   . %{_prefix}/GNUstep/System/Makefiles/GNUstep.sh
fi
%{__make} install GNUSTEP_INSTALLATION_DIR=${RPM_BUILD_ROOT}%{_prefix}/GNUstep

%ifos Linux
cat > mygnustep.init.in << EOF
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
        echo -n "Starting gnustep services: "
        daemon %{_prefix}/GNUstep/Tools/GSARCH/GSOS/gdomap
        echo
        touch /var/lock/subsys/gnustep
        ;;

  stop)
        echo -n "Stopping gnustep services: "
        killproc gdomap
        echo
        rm -f /var/lock/subsys/gnustep
        ;;

   status)
        status gdomap
        ;;

   restart|reload)
        \$0 stop
        \$0 start
        ;;

    *)
        echo "Usage: gnustep {start|stop|status|restart|reload}"
        exit 1
esac
EOF

sed -e "s|GSARCH|${GNUSTEP_HOST_CPU}|g" -e "s|GSOS|${GNUSTEP_HOST_OS}|g" < mygnustep.init.in > mygnustep.init
install -d ${RPM_BUILD_ROOT}/etc/rc.d/init.d
mv -f mygnustep.init ${RPM_BUILD_ROOT}/etc/rc.d/init.d/gnustep
%endif

cat > filelist.rpm.in << EOF
%defattr (-, root, root)
%doc ANNOUNCE AUTHORS COPYING* ChangeLog* INSTALL* NEWS README Version
%config %{_prefix}/GNUstep/Libraries/Resources/NSTimeZones/localtime
%ifos Linux
%config /etc/rc.d/init.d/gnustep
%endif

%dir %{_prefix}/GNUstep/Libraries
%dir %{_prefix}/GNUstep/Libraries/Resources
%dir %{_prefix}/GNUstep/Libraries/Resources/NSTimeZones
%dir %{_prefix}/GNUstep/Libraries/GSARCH
%dir %{_prefix}/GNUstep/Libraries/GSARCH/GSOS
%dir %{_prefix}/GNUstep/Libraries/GSARCH/GSOS/%{libcombo}
%dir %{_prefix}/GNUstep/Tools
%dir %{_prefix}/GNUstep/Tools/GSARCH
%dir %{_prefix}/GNUstep/Tools/GSARCH/GSOS
%dir %{_prefix}/GNUstep/Tools/GSARCH/GSOS/%{libcombo}

%{_prefix}/GNUstep/Libraries/Resources/NSCharacterSets
%{_prefix}/GNUstep/Libraries/Resources/NSTimeZones/README
%{_prefix}/GNUstep/Libraries/Resources/NSTimeZones/abbreviations
%{_prefix}/GNUstep/Libraries/Resources/NSTimeZones/regions
%{_prefix}/GNUstep/Libraries/Resources/NSTimeZones/zones
%{_prefix}/GNUstep/Libraries/Resources/NSTimeZones/*.m
%{_prefix}/GNUstep/Libraries/GSARCH/GSOS/%{libcombo}/lib*.so.*

%{_prefix}/GNUstep/Tools/dread
%{_prefix}/GNUstep/Tools/dwrite
%{_prefix}/GNUstep/Tools/dremove
%{_prefix}/GNUstep/Tools/gdnc
%{_prefix}/GNUstep/Tools/plparse
%{_prefix}/GNUstep/Tools/sfparse
%{_prefix}/GNUstep/Tools/pldes
%{_prefix}/GNUstep/Tools/plser
%{_prefix}/GNUstep/Tools/GSARCH/GSOS/%{libcombo}/*

%attr(4755, root, root) %{_prefix}/GNUstep/Tools/GSARCH/GSOS/gdomap

EOF

cat > filelist-devel.rpm.in  << EOF
%defattr(-, root, root)
%dir %{_prefix}/GNUstep/Headers
%dir %{_prefix}/GNUstep/Headers/gnustep

%{_prefix}/GNUstep/Headers/gnustep/Foundation
%{_prefix}/GNUstep/Headers/gnustep/base
%{_prefix}/GNUstep/Headers/gnustep/unicode
%{_prefix}/GNUstep/Headers/GSARCH
%{_prefix}/GNUstep/Libraries/GSARCH/GSOS/%{libcombo}/lib*.so

EOF

sed -e "s|GSARCH|${GNUSTEP_HOST_CPU}|" -e "s|GSOS|${GNUSTEP_HOST_OS}|" < filelist.rpm.in > filelist.rpm
sed -e "s|GSARCH|${GNUSTEP_HOST_CPU}|" -e "s|GSOS|${GNUSTEP_HOST_OS}|" < filelist-devel.rpm.in > filelist-devel.rpm

echo 'GMT' > $RPM_BUILD_ROOT/%{_prefix}/GNUstep/Libraries/Resources/NSTimeZones/localtime

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -z "$GNUSTEP_SYSTEM_ROOT" ]; then
   . %{_prefix}/GNUstep/Makefiles/GNUstep.sh
fi
grep -q '^gdomap' /etc/services || (echo "gdomap 538/tcp # GNUstep distrib objects" >> /etc/services && echo "gdomap 538/udp # GNUstep distrib objects" >> /etc/services)
%ifos Linux
grep -q '%{_prefix}/GNUstep/Libraries/$GNUSTEP_HOST_CPU/$GNUSTEP_HOST_OS/gnu-gnu-gnu-xgps' /etc/ld.so.conf || echo "%{_prefix}/GNUstep/Libraries/$GNUSTEP_HOST_CPU/$GNUSTEP_HOST_OS/%{libcombo}" >> /etc/ld.so.conf
/sbin/ldconfig
/sbin/chkconfig --add gnustep
%endif

%preun
if [ -z "$GNUSTEP_SYSTEM_ROOT" ]; then
   . %{_prefix}/GNUstep/Makefiles/GNUstep.sh
fi
if [ $1 = 0 ]; then
    /sbin/chkconfig --del gnustep
    mv -f /etc/services /etc/services.orig
    grep -v "^gdomap 538" /etc/services.orig > /etc/services
    rm -f /etc/services.orig
fi

%postun
if [ -z "$GNUSTEP_SYSTEM_ROOT" ]; then
   . %{_prefix}/GNUstep/Makefiles/GNUstep.sh
fi
if [ $1 = 0 ]; then
%ifos Linux
    mv -f /etc/ld.so.conf /etc/ld.so.conf.orig
    grep -v "^%{_prefix}/GNUstep/Libraries/$GNUSTEP_HOST_CPU/$GNUSTEP_HOST_OS/%{libcombo}$" /etc/ld.so.conf.orig > /etc/ld.so.conf
    rm -f /etc/ld.so.conf.orig
    /sbin/ldconfig
%endif
fi

%files -f filelist.rpm
%defattr(644,root,root,755)

%files -f filelist-devel.rpm devel
%defattr(644,root,root,755)
