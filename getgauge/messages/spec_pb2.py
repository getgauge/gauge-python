# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: spec.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nspec.proto\x12\x0egauge.messages\"\xf9\x03\n\tProtoSpec\x12\x13\n\x0bspecHeading\x18\x01 \x01(\t\x12(\n\x05items\x18\x02 \x03(\x0b\x32\x19.gauge.messages.ProtoItem\x12\x15\n\risTableDriven\x18\x03 \x01(\x08\x12\x39\n\x0fpreHookFailures\x18\x04 \x03(\x0b\x32 .gauge.messages.ProtoHookFailure\x12:\n\x10postHookFailures\x18\x05 \x03(\x0b\x32 .gauge.messages.ProtoHookFailure\x12\x10\n\x08\x66ileName\x18\x06 \x01(\t\x12\x0c\n\x04tags\x18\x07 \x03(\t\x12\x17\n\x0fpreHookMessages\x18\x08 \x03(\t\x12\x18\n\x10postHookMessages\x18\t \x03(\t\x12\x1a\n\x0epreHookMessage\x18\n \x03(\tB\x02\x18\x01\x12\x1b\n\x0fpostHookMessage\x18\x0b \x03(\tB\x02\x18\x01\x12\x1e\n\x12preHookScreenshots\x18\x0c \x03(\x0c\x42\x02\x18\x01\x12\x1f\n\x13postHookScreenshots\x18\r \x03(\x0c\x42\x02\x18\x01\x12\x11\n\titemCount\x18\x0e \x01(\x03\x12\x1e\n\x16preHookScreenshotFiles\x18\x0f \x03(\t\x12\x1f\n\x17postHookScreenshotFiles\x18\x10 \x03(\t\"\x92\x04\n\tProtoItem\x12\x34\n\x08itemType\x18\x01 \x01(\x0e\x32\".gauge.messages.ProtoItem.ItemType\x12\'\n\x04step\x18\x02 \x01(\x0b\x32\x19.gauge.messages.ProtoStep\x12-\n\x07\x63oncept\x18\x03 \x01(\x0b\x32\x1c.gauge.messages.ProtoConcept\x12/\n\x08scenario\x18\x04 \x01(\x0b\x32\x1d.gauge.messages.ProtoScenario\x12\x45\n\x13tableDrivenScenario\x18\x05 \x01(\x0b\x32(.gauge.messages.ProtoTableDrivenScenario\x12-\n\x07\x63omment\x18\x06 \x01(\x0b\x32\x1c.gauge.messages.ProtoComment\x12)\n\x05table\x18\x07 \x01(\x0b\x32\x1a.gauge.messages.ProtoTable\x12\'\n\x04tags\x18\x08 \x01(\x0b\x32\x19.gauge.messages.ProtoTags\x12\x10\n\x08\x66ileName\x18\t \x01(\t\"j\n\x08ItemType\x12\x08\n\x04Step\x10\x00\x12\x0b\n\x07\x43omment\x10\x01\x12\x0b\n\x07\x43oncept\x10\x02\x12\x0c\n\x08Scenario\x10\x03\x12\x17\n\x13TableDrivenScenario\x10\x04\x12\t\n\x05Table\x10\x05\x12\x08\n\x04Tags\x10\x06\"\xfe\x05\n\rProtoScenario\x12\x17\n\x0fscenarioHeading\x18\x01 \x01(\t\x12\x12\n\x06\x66\x61iled\x18\x02 \x01(\x08\x42\x02\x18\x01\x12+\n\x08\x63ontexts\x18\x03 \x03(\x0b\x32\x19.gauge.messages.ProtoItem\x12\x30\n\rscenarioItems\x18\x04 \x03(\x0b\x32\x19.gauge.messages.ProtoItem\x12\x38\n\x0epreHookFailure\x18\x05 \x01(\x0b\x32 .gauge.messages.ProtoHookFailure\x12\x39\n\x0fpostHookFailure\x18\x06 \x01(\x0b\x32 .gauge.messages.ProtoHookFailure\x12\x0c\n\x04tags\x18\x07 \x03(\t\x12\x15\n\rexecutionTime\x18\x08 \x01(\x03\x12\x13\n\x07skipped\x18\t \x01(\x08\x42\x02\x18\x01\x12\x12\n\nskipErrors\x18\n \x03(\t\x12\n\n\x02ID\x18\x0b \x01(\t\x12\x30\n\rtearDownSteps\x18\x0c \x03(\x0b\x32\x19.gauge.messages.ProtoItem\x12\"\n\x04span\x18\r \x01(\x0b\x32\x14.gauge.messages.Span\x12\x38\n\x0f\x65xecutionStatus\x18\x0e \x01(\x0e\x32\x1f.gauge.messages.ExecutionStatus\x12\x17\n\x0fpreHookMessages\x18\x0f \x03(\t\x12\x18\n\x10postHookMessages\x18\x10 \x03(\t\x12\x1a\n\x0epreHookMessage\x18\x11 \x03(\tB\x02\x18\x01\x12\x1b\n\x0fpostHookMessage\x18\x12 \x03(\tB\x02\x18\x01\x12\x1e\n\x12preHookScreenshots\x18\x13 \x03(\x0c\x42\x02\x18\x01\x12\x1f\n\x13postHookScreenshots\x18\x14 \x03(\x0c\x42\x02\x18\x01\x12\x1e\n\x16preHookScreenshotFiles\x18\x15 \x03(\t\x12\x1f\n\x17postHookScreenshotFiles\x18\x16 \x03(\t\x12\x14\n\x0cretriesCount\x18\x17 \x01(\x03\"F\n\x04Span\x12\r\n\x05start\x18\x01 \x01(\x03\x12\x0b\n\x03\x65nd\x18\x02 \x01(\x03\x12\x11\n\tstartChar\x18\x03 \x01(\x03\x12\x0f\n\x07\x65ndChar\x18\x04 \x01(\x03\"\xa8\x02\n\x18ProtoTableDrivenScenario\x12/\n\x08scenario\x18\x01 \x01(\x0b\x32\x1d.gauge.messages.ProtoScenario\x12\x15\n\rtableRowIndex\x18\x02 \x01(\x05\x12\x1d\n\x15scenarioTableRowIndex\x18\x03 \x01(\x05\x12\x19\n\x11isSpecTableDriven\x18\x04 \x01(\x08\x12\x1d\n\x15isScenarioTableDriven\x18\x05 \x01(\x08\x12\x35\n\x11scenarioDataTable\x18\x06 \x01(\x0b\x32\x1a.gauge.messages.ProtoTable\x12\x34\n\x10scenarioTableRow\x18\x07 \x01(\x0b\x32\x1a.gauge.messages.ProtoTable\"\xdc\x02\n\tProtoStep\x12\x12\n\nactualText\x18\x01 \x01(\t\x12\x12\n\nparsedText\x18\x02 \x01(\t\x12+\n\tfragments\x18\x03 \x03(\x0b\x32\x18.gauge.messages.Fragment\x12\x45\n\x13stepExecutionResult\x18\x04 \x01(\x0b\x32(.gauge.messages.ProtoStepExecutionResult\x12\x17\n\x0fpreHookMessages\x18\x05 \x03(\t\x12\x18\n\x10postHookMessages\x18\x06 \x03(\t\x12\x1e\n\x12preHookScreenshots\x18\x07 \x03(\x0c\x42\x02\x18\x01\x12\x1f\n\x13postHookScreenshots\x18\x08 \x03(\x0c\x42\x02\x18\x01\x12\x1e\n\x16preHookScreenshotFiles\x18\t \x03(\t\x12\x1f\n\x17postHookScreenshotFiles\x18\n \x03(\t\"\xb2\x01\n\x0cProtoConcept\x12.\n\x0b\x63onceptStep\x18\x01 \x01(\x0b\x32\x19.gauge.messages.ProtoStep\x12(\n\x05steps\x18\x02 \x03(\x0b\x32\x19.gauge.messages.ProtoItem\x12H\n\x16\x63onceptExecutionResult\x18\x03 \x01(\x0b\x32(.gauge.messages.ProtoStepExecutionResult\"\x19\n\tProtoTags\x12\x0c\n\x04tags\x18\x01 \x03(\t\"\xac\x01\n\x08\x46ragment\x12;\n\x0c\x66ragmentType\x18\x01 \x01(\x0e\x32%.gauge.messages.Fragment.FragmentType\x12\x0c\n\x04text\x18\x02 \x01(\t\x12,\n\tparameter\x18\x03 \x01(\x0b\x32\x19.gauge.messages.Parameter\"\'\n\x0c\x46ragmentType\x12\x08\n\x04Text\x10\x00\x12\r\n\tParameter\x10\x01\"\xef\x01\n\tParameter\x12>\n\rparameterType\x18\x01 \x01(\x0e\x32\'.gauge.messages.Parameter.ParameterType\x12\r\n\x05value\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12)\n\x05table\x18\x04 \x01(\x0b\x32\x1a.gauge.messages.ProtoTable\"Z\n\rParameterType\x12\n\n\x06Static\x10\x00\x12\x0b\n\x07\x44ynamic\x10\x01\x12\x12\n\x0eSpecial_String\x10\x02\x12\x11\n\rSpecial_Table\x10\x03\x12\t\n\x05Table\x10\x04\"\x1c\n\x0cProtoComment\x12\x0c\n\x04text\x18\x01 \x01(\t\"i\n\nProtoTable\x12.\n\x07headers\x18\x01 \x01(\x0b\x32\x1d.gauge.messages.ProtoTableRow\x12+\n\x04rows\x18\x02 \x03(\x0b\x32\x1d.gauge.messages.ProtoTableRow\"\x1e\n\rProtoTableRow\x12\r\n\x05\x63\x65lls\x18\x01 \x03(\t\"\xf6\x01\n\x18ProtoStepExecutionResult\x12=\n\x0f\x65xecutionResult\x18\x01 \x01(\x0b\x32$.gauge.messages.ProtoExecutionResult\x12\x38\n\x0epreHookFailure\x18\x02 \x01(\x0b\x32 .gauge.messages.ProtoHookFailure\x12\x39\n\x0fpostHookFailure\x18\x03 \x01(\x0b\x32 .gauge.messages.ProtoHookFailure\x12\x0f\n\x07skipped\x18\x04 \x01(\x08\x12\x15\n\rskippedReason\x18\x05 \x01(\t\"\x8b\x03\n\x14ProtoExecutionResult\x12\x0e\n\x06\x66\x61iled\x18\x01 \x01(\x08\x12\x18\n\x10recoverableError\x18\x02 \x01(\x08\x12\x14\n\x0c\x65rrorMessage\x18\x03 \x01(\t\x12\x12\n\nstackTrace\x18\x04 \x01(\t\x12\x16\n\nscreenShot\x18\x05 \x01(\x0c\x42\x02\x18\x01\x12\x15\n\rexecutionTime\x18\x06 \x01(\x03\x12\x0f\n\x07message\x18\x07 \x03(\t\x12\x41\n\terrorType\x18\x08 \x01(\x0e\x32..gauge.messages.ProtoExecutionResult.ErrorType\x12\x1d\n\x11\x66\x61ilureScreenshot\x18\t \x01(\x0c\x42\x02\x18\x01\x12\x17\n\x0bscreenshots\x18\n \x03(\x0c\x42\x02\x18\x01\x12\x1d\n\x15\x66\x61ilureScreenshotFile\x18\x0b \x01(\t\x12\x17\n\x0fscreenshotFiles\x18\x0c \x03(\t\",\n\tErrorType\x12\r\n\tASSERTION\x10\x00\x12\x10\n\x0cVERIFICATION\x10\x01\"\xa9\x01\n\x10ProtoHookFailure\x12\x12\n\nstackTrace\x18\x01 \x01(\t\x12\x14\n\x0c\x65rrorMessage\x18\x02 \x01(\t\x12\x16\n\nscreenShot\x18\x03 \x01(\x0c\x42\x02\x18\x01\x12\x15\n\rtableRowIndex\x18\x04 \x01(\x05\x12\x1d\n\x11\x66\x61ilureScreenshot\x18\x05 \x01(\x0c\x42\x02\x18\x01\x12\x1d\n\x15\x66\x61ilureScreenshotFile\x18\x06 \x01(\t\"\x8b\x05\n\x10ProtoSuiteResult\x12\x34\n\x0bspecResults\x18\x01 \x03(\x0b\x32\x1f.gauge.messages.ProtoSpecResult\x12\x38\n\x0epreHookFailure\x18\x02 \x01(\x0b\x32 .gauge.messages.ProtoHookFailure\x12\x39\n\x0fpostHookFailure\x18\x03 \x01(\x0b\x32 .gauge.messages.ProtoHookFailure\x12\x0e\n\x06\x66\x61iled\x18\x04 \x01(\x08\x12\x18\n\x10specsFailedCount\x18\x05 \x01(\x05\x12\x15\n\rexecutionTime\x18\x06 \x01(\x03\x12\x13\n\x0bsuccessRate\x18\x07 \x01(\x02\x12\x13\n\x0b\x65nvironment\x18\x08 \x01(\t\x12\x0c\n\x04tags\x18\t \x01(\t\x12\x13\n\x0bprojectName\x18\n \x01(\t\x12\x11\n\ttimestamp\x18\x0b \x01(\t\x12\x19\n\x11specsSkippedCount\x18\x0c \x01(\x05\x12\x17\n\x0fpreHookMessages\x18\r \x03(\t\x12\x18\n\x10postHookMessages\x18\x0e \x03(\t\x12\x1a\n\x0epreHookMessage\x18\x0f \x03(\tB\x02\x18\x01\x12\x1b\n\x0fpostHookMessage\x18\x10 \x03(\tB\x02\x18\x01\x12\x1e\n\x12preHookScreenshots\x18\x11 \x03(\x0c\x42\x02\x18\x01\x12\x1f\n\x13postHookScreenshots\x18\x12 \x03(\x0c\x42\x02\x18\x01\x12\x0f\n\x07\x63hunked\x18\x13 \x01(\x08\x12\x11\n\tchunkSize\x18\x14 \x01(\x03\x12\x1e\n\x16preHookScreenshotFiles\x18\x15 \x03(\t\x12\x1f\n\x17postHookScreenshotFiles\x18\x16 \x03(\t\"\xbe\x02\n\x0fProtoSpecResult\x12,\n\tprotoSpec\x18\x01 \x01(\x0b\x32\x19.gauge.messages.ProtoSpec\x12\x15\n\rscenarioCount\x18\x02 \x01(\x05\x12\x1b\n\x13scenarioFailedCount\x18\x03 \x01(\x05\x12\x0e\n\x06\x66\x61iled\x18\x04 \x01(\x08\x12\x1b\n\x13\x66\x61iledDataTableRows\x18\x05 \x03(\x05\x12\x15\n\rexecutionTime\x18\x06 \x01(\x03\x12\x0f\n\x07skipped\x18\x07 \x01(\x08\x12\x1c\n\x14scenarioSkippedCount\x18\x08 \x01(\x05\x12\x1c\n\x14skippedDataTableRows\x18\t \x03(\x05\x12%\n\x06\x65rrors\x18\n \x03(\x0b\x32\x15.gauge.messages.Error\x12\x11\n\ttimestamp\x18\x0b \x01(\t\"m\n\x13ProtoScenarioResult\x12,\n\tprotoItem\x18\x01 \x01(\x0b\x32\x19.gauge.messages.ProtoItem\x12\x15\n\rexecutionTime\x18\x02 \x01(\x03\x12\x11\n\ttimestamp\x18\x03 \x01(\t\"i\n\x0fProtoStepResult\x12,\n\tprotoItem\x18\x01 \x01(\x0b\x32\x19.gauge.messages.ProtoItem\x12\x15\n\rexecutionTime\x18\x02 \x01(\x03\x12\x11\n\ttimestamp\x18\x03 \x01(\t\"\xa1\x01\n\x05\x45rror\x12-\n\x04type\x18\x01 \x01(\x0e\x32\x1f.gauge.messages.Error.ErrorType\x12\x10\n\x08\x66ilename\x18\x02 \x01(\t\x12\x12\n\nlineNumber\x18\x03 \x01(\x05\x12\x0f\n\x07message\x18\x04 \x01(\t\"2\n\tErrorType\x12\x0f\n\x0bPARSE_ERROR\x10\x00\x12\x14\n\x10VALIDATION_ERROR\x10\x01\"W\n\x0eProtoStepValue\x12\x11\n\tstepValue\x18\x01 \x01(\t\x12\x1e\n\x16parameterizedStepValue\x18\x02 \x01(\t\x12\x12\n\nparameters\x18\x03 \x03(\t*G\n\x0f\x45xecutionStatus\x12\x0f\n\x0bNOTEXECUTED\x10\x00\x12\n\n\x06PASSED\x10\x01\x12\n\n\x06\x46\x41ILED\x10\x02\x12\x0b\n\x07SKIPPED\x10\x03\x42\\\n\x16\x63om.thoughtworks.gaugeZ1github.com/getgauge/gauge-proto/go/gauge_messages\xaa\x02\x0eGauge.Messagesb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'spec_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\026com.thoughtworks.gaugeZ1github.com/getgauge/gauge-proto/go/gauge_messages\252\002\016Gauge.Messages'
  _PROTOSPEC.fields_by_name['preHookMessage']._options = None
  _PROTOSPEC.fields_by_name['preHookMessage']._serialized_options = b'\030\001'
  _PROTOSPEC.fields_by_name['postHookMessage']._options = None
  _PROTOSPEC.fields_by_name['postHookMessage']._serialized_options = b'\030\001'
  _PROTOSPEC.fields_by_name['preHookScreenshots']._options = None
  _PROTOSPEC.fields_by_name['preHookScreenshots']._serialized_options = b'\030\001'
  _PROTOSPEC.fields_by_name['postHookScreenshots']._options = None
  _PROTOSPEC.fields_by_name['postHookScreenshots']._serialized_options = b'\030\001'
  _PROTOSCENARIO.fields_by_name['failed']._options = None
  _PROTOSCENARIO.fields_by_name['failed']._serialized_options = b'\030\001'
  _PROTOSCENARIO.fields_by_name['skipped']._options = None
  _PROTOSCENARIO.fields_by_name['skipped']._serialized_options = b'\030\001'
  _PROTOSCENARIO.fields_by_name['preHookMessage']._options = None
  _PROTOSCENARIO.fields_by_name['preHookMessage']._serialized_options = b'\030\001'
  _PROTOSCENARIO.fields_by_name['postHookMessage']._options = None
  _PROTOSCENARIO.fields_by_name['postHookMessage']._serialized_options = b'\030\001'
  _PROTOSCENARIO.fields_by_name['preHookScreenshots']._options = None
  _PROTOSCENARIO.fields_by_name['preHookScreenshots']._serialized_options = b'\030\001'
  _PROTOSCENARIO.fields_by_name['postHookScreenshots']._options = None
  _PROTOSCENARIO.fields_by_name['postHookScreenshots']._serialized_options = b'\030\001'
  _PROTOSTEP.fields_by_name['preHookScreenshots']._options = None
  _PROTOSTEP.fields_by_name['preHookScreenshots']._serialized_options = b'\030\001'
  _PROTOSTEP.fields_by_name['postHookScreenshots']._options = None
  _PROTOSTEP.fields_by_name['postHookScreenshots']._serialized_options = b'\030\001'
  _PROTOEXECUTIONRESULT.fields_by_name['screenShot']._options = None
  _PROTOEXECUTIONRESULT.fields_by_name['screenShot']._serialized_options = b'\030\001'
  _PROTOEXECUTIONRESULT.fields_by_name['failureScreenshot']._options = None
  _PROTOEXECUTIONRESULT.fields_by_name['failureScreenshot']._serialized_options = b'\030\001'
  _PROTOEXECUTIONRESULT.fields_by_name['screenshots']._options = None
  _PROTOEXECUTIONRESULT.fields_by_name['screenshots']._serialized_options = b'\030\001'
  _PROTOHOOKFAILURE.fields_by_name['screenShot']._options = None
  _PROTOHOOKFAILURE.fields_by_name['screenShot']._serialized_options = b'\030\001'
  _PROTOHOOKFAILURE.fields_by_name['failureScreenshot']._options = None
  _PROTOHOOKFAILURE.fields_by_name['failureScreenshot']._serialized_options = b'\030\001'
  _PROTOSUITERESULT.fields_by_name['preHookMessage']._options = None
  _PROTOSUITERESULT.fields_by_name['preHookMessage']._serialized_options = b'\030\001'
  _PROTOSUITERESULT.fields_by_name['postHookMessage']._options = None
  _PROTOSUITERESULT.fields_by_name['postHookMessage']._serialized_options = b'\030\001'
  _PROTOSUITERESULT.fields_by_name['preHookScreenshots']._options = None
  _PROTOSUITERESULT.fields_by_name['preHookScreenshots']._serialized_options = b'\030\001'
  _PROTOSUITERESULT.fields_by_name['postHookScreenshots']._options = None
  _PROTOSUITERESULT.fields_by_name['postHookScreenshots']._serialized_options = b'\030\001'
  _globals['_EXECUTIONSTATUS']._serialized_start=5621
  _globals['_EXECUTIONSTATUS']._serialized_end=5692
  _globals['_PROTOSPEC']._serialized_start=31
  _globals['_PROTOSPEC']._serialized_end=536
  _globals['_PROTOITEM']._serialized_start=539
  _globals['_PROTOITEM']._serialized_end=1069
  _globals['_PROTOITEM_ITEMTYPE']._serialized_start=963
  _globals['_PROTOITEM_ITEMTYPE']._serialized_end=1069
  _globals['_PROTOSCENARIO']._serialized_start=1072
  _globals['_PROTOSCENARIO']._serialized_end=1838
  _globals['_SPAN']._serialized_start=1840
  _globals['_SPAN']._serialized_end=1910
  _globals['_PROTOTABLEDRIVENSCENARIO']._serialized_start=1913
  _globals['_PROTOTABLEDRIVENSCENARIO']._serialized_end=2209
  _globals['_PROTOSTEP']._serialized_start=2212
  _globals['_PROTOSTEP']._serialized_end=2560
  _globals['_PROTOCONCEPT']._serialized_start=2563
  _globals['_PROTOCONCEPT']._serialized_end=2741
  _globals['_PROTOTAGS']._serialized_start=2743
  _globals['_PROTOTAGS']._serialized_end=2768
  _globals['_FRAGMENT']._serialized_start=2771
  _globals['_FRAGMENT']._serialized_end=2943
  _globals['_FRAGMENT_FRAGMENTTYPE']._serialized_start=2904
  _globals['_FRAGMENT_FRAGMENTTYPE']._serialized_end=2943
  _globals['_PARAMETER']._serialized_start=2946
  _globals['_PARAMETER']._serialized_end=3185
  _globals['_PARAMETER_PARAMETERTYPE']._serialized_start=3095
  _globals['_PARAMETER_PARAMETERTYPE']._serialized_end=3185
  _globals['_PROTOCOMMENT']._serialized_start=3187
  _globals['_PROTOCOMMENT']._serialized_end=3215
  _globals['_PROTOTABLE']._serialized_start=3217
  _globals['_PROTOTABLE']._serialized_end=3322
  _globals['_PROTOTABLEROW']._serialized_start=3324
  _globals['_PROTOTABLEROW']._serialized_end=3354
  _globals['_PROTOSTEPEXECUTIONRESULT']._serialized_start=3357
  _globals['_PROTOSTEPEXECUTIONRESULT']._serialized_end=3603
  _globals['_PROTOEXECUTIONRESULT']._serialized_start=3606
  _globals['_PROTOEXECUTIONRESULT']._serialized_end=4001
  _globals['_PROTOEXECUTIONRESULT_ERRORTYPE']._serialized_start=3957
  _globals['_PROTOEXECUTIONRESULT_ERRORTYPE']._serialized_end=4001
  _globals['_PROTOHOOKFAILURE']._serialized_start=4004
  _globals['_PROTOHOOKFAILURE']._serialized_end=4173
  _globals['_PROTOSUITERESULT']._serialized_start=4176
  _globals['_PROTOSUITERESULT']._serialized_end=4827
  _globals['_PROTOSPECRESULT']._serialized_start=4830
  _globals['_PROTOSPECRESULT']._serialized_end=5148
  _globals['_PROTOSCENARIORESULT']._serialized_start=5150
  _globals['_PROTOSCENARIORESULT']._serialized_end=5259
  _globals['_PROTOSTEPRESULT']._serialized_start=5261
  _globals['_PROTOSTEPRESULT']._serialized_end=5366
  _globals['_ERROR']._serialized_start=5369
  _globals['_ERROR']._serialized_end=5530
  _globals['_ERROR_ERRORTYPE']._serialized_start=5480
  _globals['_ERROR_ERRORTYPE']._serialized_end=5530
  _globals['_PROTOSTEPVALUE']._serialized_start=5532
  _globals['_PROTOSTEPVALUE']._serialized_end=5619
# @@protoc_insertion_point(module_scope)
