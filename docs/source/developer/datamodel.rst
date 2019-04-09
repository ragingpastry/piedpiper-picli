:title: Data Model

.. _datamodel:

Data Model
==========

Let's start from the initial execution point of PiCli.

Let's pretend we are calling ``picli lint``. 

:py:func:`~picli.command.lint.lint`. Lint will read the configuration file
(defaults to ``piedpiper.d/pi_global_vars.yml`` and then lookup the 
`lint` sequence from the base command module.

.. autofunction:: picli.command.lint.lint

After the sequence for the command we are running has been discovered, we will loop over
that sequence and execute the subcommands in the sequence. Since we are running ``picli lint``
we will first execute the ``style`` subcommand followed by the ``sast`` subcommand. We do this
by calling the ``execute_subcommand`` function in the base module.

.. autofunction:: picli.command.base.execute_subcommand

As described in the execute_subcommand function, we will now execute each subcommand. Again, since
we ran ``picli`` lint, we will first execute ``style``.

.. automethod:: picli.command.style.Style.execute

:py:class:`~picli.configs.style_pipe.StylePipeConfig`. The StylePipeConfig object is 
the meat-and-potatoes behind the PiCli data model. This object is what defines the 
files to pass to the remote function, how group variables and file variables are 
merged together, and how the run_config is defined. Every call to a Styler's execute 
method will utilize the StylePipeConfig object to determine how to call the remote function.

.. autoclass:: picli.configs.style_pipe.StylePipeConfig


:py:class:`~picli.configs.base_pipe.BasePipeConfig`. A Base Pipe config
object which every other PipeConfig should subclass. This is used to
pass around common pipeline configuration parameters and define a structure
for PipeConfig objects.

.. autoclass:: picli.configs.base_pipe.BasePipeConfig

The PipeConfig object will create a BaseConfig object during initialization

:py:class:`~picli.config.BaseConfig`. The Base configuration class which
holds the main configuration for an invocation of PiCli. This is used
to pass around configuration options defined in a ``piedpiper.d/pi_global_vars.yml``
file and other properties.

.. autoclass:: picli.config.BaseConfig

After ``style`` we will execute ``sast``.

.. automethod:: picli.command.sast.Sast.execute

:py:class:`~picli.configs.sast_pipe.SastPipeConfig`. A SAST Pipe config
class which subclasses the BasePipeConfig. Again, this is primary used to
set the name of the PipeConfig object which determines its type.

.. autoclass:: picli.configs.sast_pipe.SastPipeConfig


