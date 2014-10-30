""" Simplified support for rfc2812 """
# https://tools.ietf.org/html/rfc2812
import collections
missing = object()


def f(field, kwargs, default=missing):
    ''' Alias for more readable command construction '''
    if default is not missing:
        return str(kwargs.get(field, default))
    return str(kwargs[field])


def pack(field, kwargs, default=missing, sep=","):
    ''' Util for joining multiple fields with commas '''
    if default is not missing:
        value = kwargs.get(field, default)
    else:
        value = kwargs[field]
    if isinstance(value, str):
        return value
    elif isinstance(value, collections.abc.Iterable):
        return sep.join(str(f) for f in value)
    else:
        return str(value)


def pack_command(command, **kwargs):
    """ Pack a command to send to an IRC server """
    if not command:
        raise ValueError("Must provide a command")
    try:
        command = command.upper()
    except AttributeError:
        raise ValueError("Command must be a str")

    # ========================================================================
    # For each command, provide:
    #  1. a link to the definition in rfc2812
    #  2. the normalized grammar, which may not equate to the rfc grammar
    #     the normalized grammar will use the keys expected in kwargs,
    #     which usually do NOT line up with rfc2812.  They may also make
    #     optional fields which are required in rfc2812, by providing
    #     the most common or reasonable defaults.
    #  3. exhaustive examples, preferring normalized form of
    #     the rfc2812 examples
    # ========================================================================

    # ========================================================================
    # Diversions from rfc2812
    # For the most part, commands try to stay as close to the spec as
    #   is reasonable.  However, some commands unintuitively overload the
    #   positional arguments, and are inconsistent w.r.t specifying
    #   singular vs multiple values.
    # In those cases, the examples below and normalized grammar will
    #   unambiguously explain how the kwargs dict will be parsed, and
    #   what fields will be used.
    # A list of non-coforming commands and a note on their difference
    #   is kept below for ease of reference.
    #
    # ALL CMDS    RENAMED param FROM <nickname> TO <nick>
    #             RENAMED param FROM <user> TO <nick>
    #                 EXCEPT USER, OPER
    #             RENAMED param FROM <comment> TO <message>
    # ------------------------------------------------------------
    # USER        mode defaults to 0
    # MODE        split into USERMODE and CHANNELMODE.
    #             USERMODE conforms to 3.1.5 User Mode message
    #             CHANNELMODE conforms to 3.2.3
    # USERMODE    (see MODE)
    # QUIT        RENAMED param FROM <Quit Message> TO <message>
    # JOIN        param <channel> can be a list of channels
    #             param <key> can be a list of keys
    # PART        param <channel> can be a list of channels
    # CHANNELMODE (see MODE)
    # TOPIC       RENAMED param FROM <topic> TO <message>
    # NAMES       param <target> is not used.
    #             param <channel> can be a list of channels
    # LIST        param <target> is not used
    #             param <channel> can be a list of channels
    # PRIVMSG     RENAMED param FROM <msgtarget> TO <target>
    #             RENAMED param FROM <text to be sent> TO <message>
    # NOTICE      RENAMED param FROM <msgtarget> TO <target>
    #             RENAMED param FROM <text to be sent> TO <message>
    # MOTD        param <target> is not used.
    # LUSERS      param <target> is not used.
    # VERSION     param <target> is not used.
    # STATS       param <target> is not used.
    # LINKS       RENAMED param FROM <remote server> TO <remote>
    #             RENAMED param FROM <server mask> TO <mask>
    # TIME        param <target> is not used.
    # CONNECT     RENAMED param FROM <target server> TO <target>
    #             RENAMED param FROM <remote server> TO <remote>
    # TRACE       param <target> is not used.
    # ADMIN       param <target> is not used.
    # INFO        param <target> is not used.
    # SQUERY      RENAMED param FROM <servicename> TO <target>
    #             RENAMED param FROM <text> TO <message>
    # WHO         No explicit param for "o" (include in <mask>)
    # WHOIS       param <target> is not used.
    #             param <mask> can be a list of channels
    # WHOWAS      param <target> is not used.
    # PING        param <server1> is optional.
    #             ADDED optional param <message>
    # PONG        RENAMED param FROM <server> TO <server1>
    #             param <server1> is optional.
    #             ADDED optional param <message>
    # AWAY        RENAMED param FROM <text> TO <message>
    # SUMMON      param <target> is not used.
    # USERS       param <target> is not used.
    # WALLOPS     RENAMED param FROM <Text to be sent> TO <message>
    # USERHOST    param <nick> can be a list of nicks
    # ISON        param <nick> can be a list of nicks
    # ========================================================================

    # ========================================================================
    # Normalized grammar:
    # : should not be provided; it denotes the beginning of the last
    #   field, which may contain spaces
    # [] indicates an optional field
    # <> denote the key that the field will be filled with
    # because fields are filled from a dict, required fields may follow
    #   optional fields - see USER command, where mode is optional
    #   (and defaults to 0)
    # ========================================================================

    # PASS
    # https://tools.ietf.org/html/rfc2812#section-3.1.1
    # PASS <password>
    # ----------
    # PASS secretpasswordhere
    if command == "PASS":
        return "PASS " + f("password", kwargs)

    # NICK
    # https://tools.ietf.org/html/rfc2812#section-3.1.2
    # NICK <nick>
    # ----------
    # NICK Wiz
    elif command == "NICK":
        return "NICK " + f("nick", kwargs)

    # USER
    # https://tools.ietf.org/html/rfc2812#section-3.1.3
    # USER <user> [<mode>] :<realname>
    # ----------
    # USER guest 8 :Ronnie Reagan
    # USER guest :Ronnie Reagan
    elif command == "USER":
        return "USER {} {} * :{}".format(
            f("user", kwargs),
            f("mode", kwargs, 0),
            f("realname", kwargs))

    # OPER
    # https://tools.ietf.org/html/rfc2812#section-3.1.4
    # OPER <user> <password>
    # ----------
    # OPER AzureDiamond hunter2
    elif command == "OPER":
        return "OPER {} {}".format(f("user", kwargs), f("password", kwargs))

    # USERMODE (renamed from MODE)
    # https://tools.ietf.org/html/rfc2812#section-3.1.5
    # MODE <nick> [<modes>]
    # ----------
    # MODE WiZ -w
    # MODE Angel +i
    # MODE
    elif command == "USERMODE":
        return "MODE {} {}".format(f("nick", kwargs), f("modes", kwargs, ''))

    # SERVICE
    # https://tools.ietf.org/html/rfc2812#section-3.1.6
    # SERVICE <nick> <distribution> <type> :<info>
    # ----------
    # SERVICE dict *.fr 0 :French
    elif command == "SERVICE":
        return "SERVICE {} * {} {} 0 :{}".format(
            f("nick", kwargs),
            f("distribution", kwargs),
            f("type", kwargs),
            f("info", kwargs))

    # QUIT
    # https://tools.ietf.org/html/rfc2812#section-3.1.7
    # QUIT :[<message>]
    # ----------
    # QUIT :Gone to lunch
    # QUIT
    elif command == "QUIT":
        if "message" in kwargs:
            return "QUIT :" + f("message", kwargs)
        return "QUIT"

    # SQUIT
    # https://tools.ietf.org/html/rfc2812#section-3.1.8
    # SQUIT <server> [<message>]
    # ----------
    # SQUIT tolsun.oulu.fi :Bad Link
    # SQUIT tolsun.oulu.fi
    elif command == "SQUIT":
        base = "SQUIT " + f("server", kwargs)
        if "message" in kwargs:
            return base + " :" + f("message", kwargs)
        return base

    # JOIN
    # https://tools.ietf.org/html/rfc2812#section-3.2.1
    # JOIN <channel> [<key>]
    # ----------
    # JOIN #foo fookey
    # JOIN #foo
    # JOIN 0
    elif command == "JOIN":
        return "JOIN {} {}".format(pack("channel", kwargs),
                                   pack("key", kwargs, ''))

    # PART
    # https://tools.ietf.org/html/rfc2812#section-3.2.2
    # PART <channel> :[<message>]
    # ----------
    # PART #foo :I lost
    # PART #foo
    elif command == "PART":
        base = "PART " + pack("channel", kwargs)
        if "message" in kwargs:
            return base + " :" + f("message", kwargs)
        return base

    # CHANNELMODE (renamed from MODE)
    # https://tools.ietf.org/html/rfc2812#section-3.2.3
    # MODE <channel> <modes> [<params>]
    # ----------
    # MODE #Finnish +imI *!*@*.fi
    # MODE #en-ops +v WiZ
    # MODE #Fins -s
    elif command == "CHANNELMODE":
        return "MODE {} {} {}".format(f("channel", kwargs),
                                      f("modes", kwargs),
                                      f("params", kwargs, ''))

    # TOPIC
    # https://tools.ietf.org/html/rfc2812#section-3.2.4
    # TOPIC <channel> :[<message>]
    # ----------
    # TOPIC #test :New topic
    # TOPIC #test :
    # TOPIC #test
    elif command == "TOPIC":
        base = "TOPIC " + f("channel", kwargs)
        if "message" in kwargs:
            return base + " :" + f("message", kwargs)
        return base

    # NAMES
    # https://tools.ietf.org/html/rfc2812#section-3.2.5
    # NAMES [<channel>]
    # ----------
    # NAMES #twilight_zone
    # NAMES
    elif command == "NAMES":
        return "NAMES " + pack("channel", kwargs, '')

    # LIST
    # https://tools.ietf.org/html/rfc2812#section-3.2.6
    # LIST [<channel>]
    # ----------
    # LIST #twilight_zone
    # LIST
    elif command == "LIST":
        return "LIST " + pack("channel", kwargs, '')

    # INVITE
    # https://tools.ietf.org/html/rfc2812#section-3.2.7
    # INVITE <nick> <channel>
    # ----------
    # INVITE Wiz #Twilight_Zone
    elif command == "INVITE":
        return "INVITE {} {}".format(f("nick", kwargs),
                                     f("channel", kwargs))

    # KICK
    # https://tools.ietf.org/html/rfc2812#section-3.2.8
    # KICK <channel> <nick> :[<message>]
    # ----------
    # KICK #Finnish WiZ :Speaking English
    # KICK #Finnish WiZ,Wiz-Bot :Both speaking English
    # KICK #Finnish,#English WiZ,ZiW :Speaking wrong language
    elif command == "KICK":
        base = "KICK {} {}".format(pack("channel", kwargs),
                                   pack("nick", kwargs))
        if "message" in kwargs:
            return base + " :" + pack("message", kwargs)
        return base

    # PRIVMSG
    # https://tools.ietf.org/html/rfc2812#section-3.3.1
    # PRIVMSG <target> :<message>
    # ----------
    # PRIVMSG Angel :yes I'm receiving it !
    # PRIVMSG $*.fi :Server tolsun.oulu.fi rebooting.
    # PRIVMSG #Finnish :This message is in english
    elif command == "PRIVMSG":
        return "PRIVMSG {} :{}".format(f("target", kwargs),
                                       f("message", kwargs))

    # NOTICE
    # https://tools.ietf.org/html/rfc2812#section-3.3.2
    # NOTICE <target> :<message>
    # ----------
    # NOTICE Angel :yes I'm receiving it !
    # NOTICE $*.fi :Server tolsun.oulu.fi rebooting.
    # NOTICE #Finnish :This message is in english
    elif command == "NOTICE":
        return "NOTICE {} :{}".format(f("target", kwargs),
                                      f("message", kwargs))

    # MOTD
    # https://tools.ietf.org/html/rfc2812#section-3.4.1
    # MOTD
    # ----------
    # MOTD
    elif command == "MOTD":
        return "MOTD"

    # LUSERS
    # https://tools.ietf.org/html/rfc2812#section-3.4.2
    # LUSERS [<mask>]
    # ----------
    # LUSERS *.edu
    # LUSERS
    elif command == "LUSERS":
        return "LUSERS " + f("mask", kwargs, '')

    # VERSION
    # https://tools.ietf.org/html/rfc2812#section-3.4.3
    # VERSION
    # ----------
    # VERSION
    elif command == "VERSION":
        return "VERSION"

    # STATS
    # https://tools.ietf.org/html/rfc2812#section-3.4.4
    # STATS [<query>]
    # ----------
    # STATS m
    # STATS
    elif command == "STATS":
        return "STATS " + f("query", kwargs, '')

    # LINKS
    # https://tools.ietf.org/html/rfc2812#section-3.4.5
    # LINKS [<remote>] [<mask>]
    # ----------
    # LINKS *.edu *.bu.edu
    # LINKS *.au
    # LINKS
    elif command == "LINKS":
        if "remote" in kwargs:
            return "LINKS {} {}".format(f("remote", kwargs), f("mask", kwargs))
        elif "mask" in kwargs:
            return "LINKS " + f("mask", kwargs)
        return "LINKS"

    # TIME
    # https://tools.ietf.org/html/rfc2812#section-3.4.6
    # TIME
    # ----------
    # TIME
    elif command == "TIME":
        return "TIME"

    # CONNECT
    # https://tools.ietf.org/html/rfc2812#section-3.4.7
    # CONNECT <target> <port> [<remote>]
    # ----------
    # CONNECT tolsun.oulu.fi 6667 *.edu
    # CONNECT tolsun.oulu.fi 6667
    elif command == "CONNECT":
        return "CONNECT {} {} {}".format(f("target", kwargs),
                                         f("port", kwargs),
                                         f("remote", kwargs, ''))

    # TRACE
    # https://tools.ietf.org/html/rfc2812#section-3.4.8
    # TRACE
    # ----------
    # TRACE
    elif command == "TRACE":
        return "TRACE"

    # ADMIN
    # https://tools.ietf.org/html/rfc2812#section-3.4.9
    # ADMIN
    # ----------
    # ADMIN
    elif command == "ADMIN":
        return "ADMIN"

    # INFO
    # https://tools.ietf.org/html/rfc2812#section-3.4.10
    # INFO
    # ----------
    # INFO
    elif command == "INFO":
        return "INFO"

    # SERVLIST
    # https://tools.ietf.org/html/rfc2812#section-3.5.1
    # SERVLIST [<mask>] [<type>]
    # ----------
    # SERVLIST *SERV 3
    # SERVLIST *SERV
    # SERVLIST
    elif command == "SERVLIST":
        return "SERVLIST {} {}".format(f("mask", kwargs, ''),
                                       f("type", kwargs, ''))

    # SQUERY
    # https://tools.ietf.org/html/rfc2812#section-3.5.2
    # SQUERY <target> :<message>
    # ----------
    # SQUERY irchelp :HELP privmsg
    elif command == "SQUERY":
        return "SQUERY {} :{}".format(f("target", kwargs),
                                      f("message", kwargs))

    # WHO
    # https://tools.ietf.org/html/rfc2812#section-3.6.1
    # WHO [<mask>]
    # ----------
    # WHO jto* o
    # WHO *.fi
    # WHO
    elif command == "WHO":
        return "WHO " + f("mask", kwargs, '')

    # WHOIS
    # https://tools.ietf.org/html/rfc2812#section-3.6.2
    # WHOIS <mask>
    # ----------
    # WHOIS jto* o
    # WHOIS *.fi
    elif command == "WHOIS":
        return "WHOIS " + f("mask", kwargs)

    # WHOWAS
    # https://tools.ietf.org/html/rfc2812#section-3.6.3
    # WHOWAS <nick> [<count>]
    # ----------
    # WHOWAS Wiz 9
    # WHOWAS Mermaid
    elif command == "WHOWAS":
        return "WHOWAS {} {}".format(pack("nick", kwargs),
                                     f("count", kwargs, ''))

    # KILL
    # https://tools.ietf.org/html/rfc2812#section-3.7.1
    # KILL <nick> :<message>
    # ----------
    # KILL WiZ :Spamming joins
    elif command == "KILL":
        return "KILL {} :{}".format(f("nick", kwargs), f("message", kwargs))

    # PING
    # https://tools.ietf.org/html/rfc2812#section-3.7.3
    # PING [<server1>] [<server2>] :[<message>]
    # ----------
    # PING csd.bu.edu tolsun.oulu.fi :Keepalive
    # PING csd.bu.edu :I'm still here
    # PING :I'm still here
    # PING
    elif command == "PING":
        message = "PING {} {}".format(f("server1", kwargs, ''),
                                      f("server2", kwargs, ''))
        if "message" in kwargs:
            message += " :" + f("message", kwargs)
        return message

    # PONG
    # https://tools.ietf.org/html/rfc2812#section-3.7.3
    # PONG [<server1>] [<server2>] :[<message>]
    # ----------
    # PONG csd.bu.edu tolsun.oulu.fi :Keepalive
    # PONG csd.bu.edu :I'm still here
    # PONG :I'm still here
    # PONG
    elif command == "PONG":
        message = "PONG {} {}".format(f("server1", kwargs, ''),
                                      f("server2", kwargs, ''))
        if "message" in kwargs:
            message += " :" + f("message", kwargs)
        return message

    # AWAY
    # https://tools.ietf.org/html/rfc2812#section-4.1
    # AWAY :[<message>]
    # ----------
    # AWAY :Gone to lunch.
    # AWAY
    elif command == "AWAY":
        if "message" in kwargs:
            return "AWAY :" + f("message", kwargs)
        return "AWAY"

    # REHASH
    # https://tools.ietf.org/html/rfc2812#section-4.2
    # REHASH
    # ----------
    # REHASH
    elif command == "REHASH":
        return "REHASH"

    # DIE
    # https://tools.ietf.org/html/rfc2812#section-4.3
    # DIE
    # ----------
    # DIE
    elif command == "DIE":
        return "DIE"

    # RESTART
    # https://tools.ietf.org/html/rfc2812#section-4.4
    # RESTART
    # ----------
    # RESTART
    elif command == "RESTART":
        return "RESTART"

    # SUMMON
    # https://tools.ietf.org/html/rfc2812#section-4.5
    # SUMMON <nick> [<channel>]
    # ----------
    # SUMMON Wiz #Finnish
    # SUMMON Wiz
    elif command == "SUMMON":
        return "SUMMON {} {}".format(f("nick", kwargs),
                                     f("channel", kwargs, ''))

    # USERS
    # https://tools.ietf.org/html/rfc2812#section-4.6
    # USERS
    # ----------
    # USERS
    elif command == "USERS":
        return "USERS"

    # WALLOPS
    # https://tools.ietf.org/html/rfc2812#section-4.7
    # WALLOPS :<message>
    # ----------
    # WALLOPS :Maintenance in 5 minutes
    elif command == "WALLOPS":
        return "WALLOPS :" + f("message", kwargs)

    # USERHOST
    # https://tools.ietf.org/html/rfc2812#section-4.8
    # USERHOST <nick>
    # ----------
    # USERHOST Wiz Michael syrk
    # USERHOST syrk
    elif command == "USERHOST":
        return "USERHOST " + pack("nick", kwargs, sep=" ")

    # ISON
    # https://tools.ietf.org/html/rfc2812#section-4.9
    # ISON <nick>
    # ----------
    # ISON Wiz Michael syrk
    # ISON syrk
    elif command == "ISON":
        return "ISON " + pack("nick", kwargs, sep=" ")

    else:
        raise ValueError("Unknown command '{}'".format(command))
