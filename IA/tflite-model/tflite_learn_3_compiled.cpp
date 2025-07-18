/*
 * Copyright (c) 2025 EdgeImpulse Inc.
 *
 * Generated by Edge Impulse and licensed under the applicable Edge Impulse
 * Terms of Service. Community and Professional Terms of Service
 * (https://edgeimpulse.com/legal/terms-of-service) or Enterprise Terms of
 * Service (https://edgeimpulse.com/legal/enterprise-terms-of-service),
 * according to your product plan subscription (the “License”).
 *
 * This software, documentation and other associated files (collectively referred
 * to as the “Software”) is a single SDK variation generated by the Edge Impulse
 * platform and requires an active paid Edge Impulse subscription to use this
 * Software for any purpose.
 *
 * You may NOT use this Software unless you have an active Edge Impulse subscription
 * that meets the eligibility requirements for the applicable License, subject to
 * your full and continued compliance with the terms and conditions of the License,
 * including without limitation any usage restrictions under the applicable License.
 *
 * If you do not have an active Edge Impulse product plan subscription, or if use
 * of this Software exceeds the usage limitations of your Edge Impulse product plan
 * subscription, you are not permitted to use this Software and must immediately
 * delete and erase all copies of this Software within your control or possession.
 * Edge Impulse reserves all rights and remedies available to enforce its rights.
 *
 * Unless required by applicable law or agreed to in writing, the Software is
 * distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
 * either express or implied. See the License for the specific language governing
 * permissions, disclaimers and limitations under the License.
 */
// Generated on: 11.07.2025 19:33:41

#include <stdio.h>
#include <stdlib.h>
#include "edge-impulse-sdk/tensorflow/lite/c/builtin_op_data.h"
#include "edge-impulse-sdk/tensorflow/lite/c/common.h"
#include "edge-impulse-sdk/tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "edge-impulse-sdk/porting/ei_classifier_porting.h"

#if EI_CLASSIFIER_PRINT_STATE
#if defined(__cplusplus) && EI_C_LINKAGE == 1
extern "C" {
    extern void ei_printf(const char *format, ...);
}
#else
extern void ei_printf(const char *format, ...);
#endif
#endif

#define STRINGIZE(x) #x
#define STRINGIZE_VALUE_OF(x) STRINGIZE(x)

#if defined (__GNUC__)  /* GNU compiler */
#define ALIGN(X) __attribute__((aligned(X)))
#define DEFINE_SECTION(x) __attribute__((section(x)))
#elif defined (_MSC_VER)
#define ALIGN(X) __declspec(align(X))
#elif defined (__TASKING__) /* TASKING Compiler */
#define ALIGN(X) __align(X)
#define DEFINE_SECTION(x) __attribute__((section(x)))
#elif defined (__ARMCC_VERSION) /* Arm Compiler */
#define ALIGN(X) __ALIGNED(x)
#define DEFINE_SECTION(x) __attribute__((section(x)))
#elif defined (__ICCARM__) /* IAR Compiler */
#define ALIGN(x) __attribute__((aligned(x)))
#define DEFINE_SECTION(x) __attribute__((section(x)))
#elif defined (__clang__) /* LLVM/Clang Compiler */
#define ALIGN(X) __ALIGNED(x)
#define DEFINE_SECTION(x) __attribute__((section(x)))
#endif

#if defined(EI_MODEL_SECTION) && (defined(__GNUC__) || defined(__clang__))
#define MODEL_SECTION(X) __attribute__((section(STRINGIZE_VALUE_OF(X))))
#else
#define MODEL_SECTION(X)
#endif

#ifndef EI_MAX_SCRATCH_BUFFER_COUNT
#ifndef CONFIG_IDF_TARGET_ESP32S3
#define EI_MAX_SCRATCH_BUFFER_COUNT 4
#else
#define EI_MAX_SCRATCH_BUFFER_COUNT 8
#endif // CONFIG_IDF_TARGET_ESP32S3
#endif // EI_MAX_SCRATCH_BUFFER_COUNT

#ifndef EI_MAX_OVERFLOW_BUFFER_COUNT
#define EI_MAX_OVERFLOW_BUFFER_COUNT 10
#endif // EI_MAX_OVERFLOW_BUFFER_COUNT

using namespace tflite;
using namespace tflite::ops;
using namespace tflite::ops::micro;

namespace {

#if defined(EI_CLASSIFIER_ALLOCATION_STATIC_HIMAX) || defined(EI_CLASSIFIER_ALLOCATION_STATIC_HIMAX_GNU)
constexpr int kTensorArenaSize = 3200;
#else
constexpr int kTensorArenaSize = 2176;
#endif

#if defined(EI_CLASSIFIER_ALLOCATION_STATIC)
#if defined (EI_TENSOR_ARENA_LOCATION)
uint8_t tensor_arena[kTensorArenaSize] ALIGN(16) DEFINE_SECTION(STRINGIZE_VALUE_OF(EI_TENSOR_ARENA_LOCATION));
#else
uint8_t tensor_arena[kTensorArenaSize] ALIGN(16);
#endif
#elif defined(EI_CLASSIFIER_ALLOCATION_STATIC_HIMAX)
#pragma Bss(".tensor_arena")
uint8_t tensor_arena[kTensorArenaSize] ALIGN(16);
#pragma Bss()
#elif defined(EI_CLASSIFIER_ALLOCATION_STATIC_HIMAX_GNU)
uint8_t tensor_arena[kTensorArenaSize] ALIGN(16) __attribute__((section(".tensor_arena")));
#else
#define EI_CLASSIFIER_ALLOCATION_HEAP 1
uint8_t* tensor_arena = NULL;
#endif

static uint8_t* tensor_boundary;
static uint8_t* current_location;

template <int SZ, class T> struct TfArray {
  int sz; T elem[SZ];
};

enum used_operators_e {
  OP_RESHAPE, OP_CONV_2D, OP_MAX_POOL_2D, OP_FULLY_CONNECTED, OP_SOFTMAX,  OP_LAST
};

struct TensorInfo_t { // subset of TfLiteTensor used for initialization from constant memory
  TfLiteAllocationType allocation_type;
  TfLiteType type;
  void* data;
  TfLiteIntArray* dims;
  size_t bytes;
  TfLiteQuantization quantization;
};

typedef struct {
  TfLiteTensor tensor;
  int16_t index;
} TfLiteTensorWithIndex;

typedef struct {
  TfLiteEvalTensor tensor;
  int16_t index;
} TfLiteEvalTensorWithIndex;

TfLiteContext ctx{};
static const int MAX_TFL_TENSOR_COUNT = 4;
static TfLiteTensorWithIndex tflTensors[MAX_TFL_TENSOR_COUNT];
static const int MAX_TFL_EVAL_COUNT = 4;
static TfLiteEvalTensorWithIndex tflEvalTensors[MAX_TFL_EVAL_COUNT];
TfLiteRegistration registrations[OP_LAST];

namespace g0 {
const TfArray<2, int> tensor_dimension0 = { 2, { 1,650 } };
const TfArray<1, float> quant0_scale = { 1, { 0.04728081077337265, } };
const TfArray<1, int> quant0_zero = { 1, { 20 } };
const TfLiteAffineQuantization quant0 = { (TfLiteFloatArray*)&quant0_scale, (TfLiteIntArray*)&quant0_zero, 0 };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(16) int32_t tensor_data1[4] = { 1, 1, 50, 13, };
const TfArray<1, int> tensor_dimension1 = { 1, { 4 } };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(16) int32_t tensor_data2[4] = { 1, 50, 1, 8, };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(16) int32_t tensor_data3[4] = { 1, 1, 25, 8, };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(16) int32_t tensor_data4[4] = { 1, 25, 1, 16, };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(8) int32_t tensor_data5[2] = { -1, 208, };
const TfArray<1, int> tensor_dimension5 = { 1, { 2 } };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(8) int32_t tensor_data6[2] = { 4795, -4795, };
const TfArray<1, float> quant6_scale = { 1, { 6.4166095398832113e-05, } };
const TfArray<1, int> quant6_zero = { 1, { 0 } };
const TfLiteAffineQuantization quant6 = { (TfLiteFloatArray*)&quant6_scale, (TfLiteIntArray*)&quant6_zero, 0 };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(16) int8_t tensor_data7[2*208] = { 
  -2, -50, 11, 23, 2, -1, -54, -36, 32, 74, 40, -31, -38, 31, -30, 15, -2, -34, -16, -77, -40, 85, -6, 41, -6, 31, 34, 56, -5, 11, -56, -24, -30, -10, -20, -47, -78, -9, 50, 55, 15, 57, -19, 48, -29, 2, -81, -76, -23, -64, -24, -61, -33, 12, -22, -8, -22, -40, -14, 85, -13, -3, -66, -38, -24, -54, -7, -80, -32, 48, -70, 35, -7, 16, -39, 8, -43, -34, -1, -80, -46, -11, -61, -10, -44, 0, 4, 37, 53, 11, -43, 67, -22, -69, -59, -44, -27, -9, -15, -49, 7, 36, -26, 0, 21, 46, 14, 77, -98, -57, -23, -43, -77, -33, -53, -29, -29, 15, -67, -35, 13, -21, -14, 64, -21, -38, -7, -86, -10, 7, -94, -4, -44, 53, 3, -12, -3, 24, -33, 84, -13, -77, -60, -57, -32, -73, -32, -57, -71, 84, -68, 28, -2, 5, -89, 46, -20, -37, -28, -68, -36, -7, -32, -34, -64, 20, 74, 58, 24, 29, -44, 96, -10, -24, 22, -70, 5, -40, 8, -50, -48, 68, 11, 21, 58, -4, 80, 37, -2, -15, -33, -93, -37, -27, 36, -54, 39, 7, 8, 32, 10, 23, 3, 13, 48, -83, -52, -7, 
  60, 14, 9, 11, 9, -32, -13, 15, -67, -23, -123, -33, -8, 54, 33, -3, 34, 19, 46, -2, 104, -75, 14, 2, 15, -77, 2, -78, 23, 52, 36, 115, 47, 66, 54, -14, 49, -85, -2, 26, -37, 24, -31, -53, 2, 51, 35, 60, 67, 31, 43, -17, 53, -19, 93, -38, -5, -45, 87, -46, -6, -31, 1, 20, 38, 68, 9, 88, 11, -32, 20, -42, 26, -8, -6, -66, -1, 25, 7, 63, 17, -6, 37, 15, 39, -39, 36, -39, -70, -2, 67, -47, 11, 36, -15, 54, 76, 60, 84, 44, 52, -25, 31, 32, -53, 2, -71, -41, 48, 34, 16, 5, 67, 81, 34, 80, 95, -27, 68, -59, -51, -59, 19, -34, 70, -18, 81, 30, -15, 16, 53, 36, 51, -9, 45, -23, -52, -12, 27, -41, 73, 85, 11, 80, -11, 26, 8, 112, 94, -10, 3, 14, 16, -63, 127, -68, 28, 52, -20, 18, -7, -4, 16, 57, 25, -60, -34, 22, -49, -19, -17, -65, 15, 11, 23, 48, 58, 30, 58, 78, 72, -64, -23, -39, -87, -83, -101, -81, -12, 34, -44, 2, 35, 21, 0, -9, 12, -29, 8, -52, -31, -45, 23, -74, -40, 4, 17, 7, 
};
const TfArray<2, int> tensor_dimension7 = { 2, { 2,208 } };
const TfArray<1, float> quant7_scale = { 1, { 0.0032354709692299366, } };
const TfLiteAffineQuantization quant7 = { (TfLiteFloatArray*)&quant7_scale, (TfLiteIntArray*)&g0::quant6_zero, 0 };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(16) int32_t tensor_data8[16] = { -1213, -1086, -1373, -1098, -1214, 940, -1325, -1100, 892, 484, -903, 3589, -823, -785, -544, -800, };
const TfArray<1, int> tensor_dimension8 = { 1, { 16 } };
const TfArray<16, float> quant8_scale = { 16, { 0.00012400826381053776, 0.00018517421267461032, 0.00019597080245148391, 0.00017935264622792602, 0.00018977391300722957, 0.0001443125365767628, 0.00014514417853206396, 0.00012951037206221372, 0.00017299973114859313, 0.00014344167720992118, 0.00018861687567550689, 0.00013135500194039196, 0.00012212885485496372, 0.00016239819524344057, 0.00015358271775767207, 0.00017905374988913536, } };
const TfArray<16, int> quant8_zero = { 16, { 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 } };
const TfLiteAffineQuantization quant8 = { (TfLiteFloatArray*)&quant8_scale, (TfLiteIntArray*)&quant8_zero, 0 };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(16) int8_t tensor_data9[16*1*3*8] = { 
  /* [0][0][][] */ 1,52,127,-3,-29,-64,-64,-22, -120,38,-34,-62,-41,-20,101,-112, -49,62,78,-11,-32,-58,125,-4, 
  /* [1][0][][] */ -88,26,-15,-14,-23,-35,-77,-22, -102,-82,8,4,21,4,127,22, 64,-15,45,-25,-22,-31,-20,-20, 
  /* [2][0][][] */ -25,12,-19,-27,-21,-13,74,14, 127,-1,56,-19,-18,-7,-53,10, -56,-6,46,-54,-32,-18,74,-4, 
  /* [3][0][][] */ 127,-75,38,-81,18,-39,-104,78, -8,-32,-21,-26,-24,-45,-32,38, -68,-1,-18,-84,-22,20,84,36, 
  /* [4][0][][] */ -110,-11,-46,-44,-43,-29,55,38, -59,-51,-17,-48,-28,5,52,13, 127,-20,53,-4,-48,-26,-53,39, 
  /* [5][0][][] */ -56,-73,-57,75,-4,-27,-18,89, -78,-19,-124,-28,127,124,-47,-56, -84,7,-67,67,45,99,-65,-1, 
  /* [6][0][][] */ 96,39,-5,45,-119,-36,62,-34, 35,-75,15,-37,-19,7,34,-18, -2,-74,-110,48,2,26,-127,-122, 
  /* [7][0][][] */ 0,71,9,-95,-121,116,-27,-17, -10,27,-29,127,48,13,-2,-44, -77,-84,-88,-76,87,-7,25,-54, 
  /* [8][0][][] */ 28,-123,-16,66,22,-17,-6,24, -46,-127,-71,36,-24,-22,-75,55, -32,-103,-7,96,-11,65,-73,-36, 
  /* [9][0][][] */ -25,-84,-23,23,-127,95,-11,67, -40,-30,-50,-47,25,70,-24,49, -42,-84,-73,99,12,86,-44,47, 
  /* [10][0][][] */ -61,-72,-87,-28,-50,-109,26,-20, -23,-115,4,2,5,-79,-34,39, -39,-81,-4,43,-73,63,-51,127, 
  /* [11][0][][] */ -58,-1,-95,109,109,126,-51,-48, -59,-127,-87,10,90,-69,-64,4, -40,-110,-85,66,-28,-29,-46,-109, 
  /* [12][0][][] */ -127,89,-109,61,-71,-86,102,-92, 60,-12,-105,-42,-101,42,-112,-94, 24,40,62,-20,-24,-100,-70,49, 
  /* [13][0][][] */ 10,-32,-22,-57,-77,12,-3,-30, 36,38,-49,-59,-23,-14,-69,-17, -127,-39,107,-55,33,-14,-94,52, 
  /* [14][0][][] */ -57,8,39,-40,-73,-46,35,-76, -27,22,117,-3,4,-15,80,-66, 114,4,-2,1,-7,-55,-46,-127, 
  /* [15][0][][] */ 43,-28,-34,-72,-26,-42,-17,60, -56,-22,45,-44,-47,-37,25,35, -27,-23,127,-55,-9,-11,73,41, 
};
const TfArray<4, int> tensor_dimension9 = { 4, { 16,1,3,8 } };
const TfArray<16, float> quant9_scale = { 16, { 0.0026029546279460192, 0.0038868382107466459, 0.0041134604252874851, 0.0037646426353603601, 0.003983386792242527, 0.0030291446018964052, 0.0030466010794043541, 0.0027184446807950735, 0.003631293773651123, 0.0030108650680631399, 0.0039591002278029919, 0.0027571639511734247, 0.0025635054334998131, 0.0034087658859789371, 0.0032237272243946791, 0.0037583685480058193, } };
const TfLiteAffineQuantization quant9 = { (TfLiteFloatArray*)&quant9_scale, (TfLiteIntArray*)&g0::quant8_zero, 0 };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(16) int32_t tensor_data10[8] = { -1440, -1878, -2573, -1800, -1725, -2884, -3024, -1575, };
const TfArray<1, int> tensor_dimension10 = { 1, { 8 } };
const TfArray<8, float> quant10_scale = { 8, { 0.00024361540272366256, 0.0001629881007829681, 0.00018824677681550384, 0.00015334037016145885, 0.00016555006732232869, 0.00016426533693447709, 0.00019925329252146184, 0.0001794687268557027, } };
const TfArray<8, int> quant10_zero = { 8, { 0,0,0,0,0,0,0,0 } };
const TfLiteAffineQuantization quant10 = { (TfLiteFloatArray*)&quant10_scale, (TfLiteIntArray*)&quant10_zero, 0 };
const MODEL_SECTION(EI_MODEL_SECTION) ALIGN(16) int8_t tensor_data11[8*1*3*13] = { 
  /* [0][0][][] */ -25,-48,21,50,-91,38,32,-55,-34,-16,4,-46,14, -39,-127,78,84,-29,30,-5,-6,-26,-1,-13,24,-35, -18,-122,8,98,-49,11,65,-2,-10,17,-8,-21,-18, 
  /* [1][0][][] */ -86,-82,-35,4,-32,121,-34,114,24,-17,36,-14,39, -75,4,13,-115,21,92,55,55,-24,31,4,37,39, -52,-44,-28,-52,20,-25,13,127,21,-20,-98,-71,-26, 
  /* [2][0][][] */ 127,88,28,-21,-68,-89,-1,15,14,41,28,-46,37, -32,-54,97,44,-69,-22,24,32,40,-55,-40,10,31, -81,-40,76,3,-105,-10,-23,115,80,-8,-40,-58,24, 
  /* [3][0][][] */ -78,-107,4,-54,30,-43,69,-77,30,-4,-4,-3,33, -27,-54,50,71,88,-127,77,-54,90,5,55,-22,-12, -36,-61,99,-18,6,-47,84,-47,-3,14,-51,6,64, 
  /* [4][0][][] */ 44,-8,-64,92,4,57,12,40,-44,-7,-2,-28,-52, -5,-99,105,-127,-26,7,-74,13,-3,-57,17,-70,78, 64,-33,-8,-31,29,33,-42,0,85,-42,4,15,-7, 
  /* [5][0][][] */ 33,92,-64,46,-37,27,23,11,-89,30,0,-51,-13, -12,-40,1,-54,-52,9,-19,-74,26,83,-55,-57,62, -20,13,-63,81,-72,44,4,-97,127,-29,-59,-24,55, 
  /* [6][0][][] */ 87,52,-21,-9,84,15,-31,-40,-31,0,20,22,-7, 4,61,2,-88,36,48,-74,18,64,13,36,-8,18, 59,59,64,-55,14,-27,-12,-33,9,39,24,127,-13, 
  /* [7][0][][] */ 68,-57,86,43,46,48,-46,13,-63,5,57,-127,28, -40,23,-29,20,57,15,19,-75,8,-22,-8,16,-60, -15,84,8,42,0,-28,29,10,14,-9,8,-76,48, 
};
const TfArray<4, int> tensor_dimension11 = { 4, { 8,1,3,13 } };
const TfArray<8, float> quant11_scale = { 8, { 0.0051525216549634933, 0.0034472357947379351, 0.0039814626798033714, 0.0032431839499622583, 0.0035014217719435692, 0.003474249504506588, 0.0042142528109252453, 0.0037958046887069941, } };
const TfLiteAffineQuantization quant11 = { (TfLiteFloatArray*)&quant11_scale, (TfLiteIntArray*)&g0::quant10_zero, 0 };
const TfArray<4, int> tensor_dimension12 = { 4, { 1,1,50,13 } };
const TfArray<4, int> tensor_dimension13 = { 4, { 1,1,50,8 } };
const TfArray<1, float> quant13_scale = { 1, { 0.047641348093748093, } };
const TfArray<1, int> quant13_zero = { 1, { -128 } };
const TfLiteAffineQuantization quant13 = { (TfLiteFloatArray*)&quant13_scale, (TfLiteIntArray*)&quant13_zero, 0 };
const TfArray<4, int> tensor_dimension14 = { 4, { 1,50,1,8 } };
const TfArray<4, int> tensor_dimension15 = { 4, { 1,25,1,8 } };
const TfArray<4, int> tensor_dimension16 = { 4, { 1,1,25,8 } };
const TfArray<4, int> tensor_dimension17 = { 4, { 1,1,25,16 } };
const TfArray<1, float> quant17_scale = { 1, { 0.019832072779536247, } };
const TfLiteAffineQuantization quant17 = { (TfLiteFloatArray*)&quant17_scale, (TfLiteIntArray*)&g0::quant13_zero, 0 };
const TfArray<4, int> tensor_dimension18 = { 4, { 1,25,1,16 } };
const TfArray<4, int> tensor_dimension19 = { 4, { 1,13,1,16 } };
const TfArray<2, int> tensor_dimension20 = { 2, { 1,208 } };
const TfArray<2, int> tensor_dimension21 = { 2, { 1,2 } };
const TfArray<1, float> quant21_scale = { 1, { 0.05155307799577713, } };
const TfArray<1, int> quant21_zero = { 1, { -3 } };
const TfLiteAffineQuantization quant21 = { (TfLiteFloatArray*)&quant21_scale, (TfLiteIntArray*)&quant21_zero, 0 };
const TfArray<1, float> quant22_scale = { 1, { 0.00390625, } };
const TfLiteAffineQuantization quant22 = { (TfLiteFloatArray*)&quant22_scale, (TfLiteIntArray*)&g0::quant13_zero, 0 };
const TfLiteReshapeParams opdata0 = { { 0, 0, 0, 0, 0, 0, 0, 0, }, 0 };
const TfArray<2, int> inputs0 = { 2, { 0,1 } };
const TfArray<1, int> outputs0 = { 1, { 12 } };
const TfLiteConvParams opdata1 = { kTfLitePaddingSame, 1,1, kTfLiteActRelu, 1,1 };
const TfArray<3, int> inputs1 = { 3, { 12,11,10 } };
const TfArray<1, int> outputs1 = { 1, { 13 } };
const TfLiteReshapeParams opdata2 = { { 0, 0, 0, 0, 0, 0, 0, 0, }, 0 };
const TfArray<2, int> inputs2 = { 2, { 13,2 } };
const TfArray<1, int> outputs2 = { 1, { 14 } };
const TfLitePoolParams opdata3 = { kTfLitePaddingSame, 1,2, 1,2, kTfLiteActNone, { { 0,0, 0, 0 } } };
const TfArray<1, int> inputs3 = { 1, { 14 } };
const TfArray<1, int> outputs3 = { 1, { 15 } };
const TfLiteReshapeParams opdata4 = { { 0, 0, 0, 0, 0, 0, 0, 0, }, 0 };
const TfArray<2, int> inputs4 = { 2, { 15,3 } };
const TfArray<1, int> outputs4 = { 1, { 16 } };
const TfLiteConvParams opdata5 = { kTfLitePaddingSame, 1,1, kTfLiteActRelu, 1,1 };
const TfArray<3, int> inputs5 = { 3, { 16,9,8 } };
const TfArray<1, int> outputs5 = { 1, { 17 } };
const TfLiteReshapeParams opdata6 = { { 0, 0, 0, 0, 0, 0, 0, 0, }, 0 };
const TfArray<2, int> inputs6 = { 2, { 17,4 } };
const TfArray<1, int> outputs6 = { 1, { 18 } };
const TfLitePoolParams opdata7 = { kTfLitePaddingSame, 1,2, 1,2, kTfLiteActNone, { { 0,0, 0, 0 } } };
const TfArray<1, int> inputs7 = { 1, { 18 } };
const TfArray<1, int> outputs7 = { 1, { 19 } };
const TfLiteReshapeParams opdata8 = { { 0, 0, 0, 0, 0, 0, 0, 0, }, 0 };
const TfArray<2, int> inputs8 = { 2, { 19,5 } };
const TfArray<1, int> outputs8 = { 1, { 20 } };
const TfLiteFullyConnectedParams opdata9 = { kTfLiteActNone, kTfLiteFullyConnectedWeightsFormatDefault, false, false };
const TfArray<3, int> inputs9 = { 3, { 20,7,6 } };
const TfArray<1, int> outputs9 = { 1, { 21 } };
const TfLiteSoftmaxParams opdata10 = { 1 };
const TfArray<1, int> inputs10 = { 1, { 21 } };
const TfArray<1, int> outputs10 = { 1, { 22 } };
};

TensorInfo_t tensorData[] = {
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 656), (TfLiteIntArray*)&g0::tensor_dimension0, 650, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant0))}, },
{ kTfLiteMmapRo, kTfLiteInt32, (int32_t*)g0::tensor_data1, (TfLiteIntArray*)&g0::tensor_dimension1, 16, {kTfLiteNoQuantization, nullptr}, },
{ kTfLiteMmapRo, kTfLiteInt32, (int32_t*)g0::tensor_data2, (TfLiteIntArray*)&g0::tensor_dimension1, 16, {kTfLiteNoQuantization, nullptr}, },
{ kTfLiteMmapRo, kTfLiteInt32, (int32_t*)g0::tensor_data3, (TfLiteIntArray*)&g0::tensor_dimension1, 16, {kTfLiteNoQuantization, nullptr}, },
{ kTfLiteMmapRo, kTfLiteInt32, (int32_t*)g0::tensor_data4, (TfLiteIntArray*)&g0::tensor_dimension1, 16, {kTfLiteNoQuantization, nullptr}, },
{ kTfLiteMmapRo, kTfLiteInt32, (int32_t*)g0::tensor_data5, (TfLiteIntArray*)&g0::tensor_dimension5, 8, {kTfLiteNoQuantization, nullptr}, },
{ kTfLiteMmapRo, kTfLiteInt32, (int32_t*)g0::tensor_data6, (TfLiteIntArray*)&g0::tensor_dimension5, 8, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant6))}, },
{ kTfLiteMmapRo, kTfLiteInt8, (int32_t*)g0::tensor_data7, (TfLiteIntArray*)&g0::tensor_dimension7, 416, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant7))}, },
{ kTfLiteMmapRo, kTfLiteInt32, (int32_t*)g0::tensor_data8, (TfLiteIntArray*)&g0::tensor_dimension8, 64, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant8))}, },
{ kTfLiteMmapRo, kTfLiteInt8, (int32_t*)g0::tensor_data9, (TfLiteIntArray*)&g0::tensor_dimension9, 384, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant9))}, },
{ kTfLiteMmapRo, kTfLiteInt32, (int32_t*)g0::tensor_data10, (TfLiteIntArray*)&g0::tensor_dimension10, 32, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant10))}, },
{ kTfLiteMmapRo, kTfLiteInt8, (int32_t*)g0::tensor_data11, (TfLiteIntArray*)&g0::tensor_dimension11, 312, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant11))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 0), (TfLiteIntArray*)&g0::tensor_dimension12, 650, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant0))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 656), (TfLiteIntArray*)&g0::tensor_dimension13, 400, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant13))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 0), (TfLiteIntArray*)&g0::tensor_dimension14, 400, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant13))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 400), (TfLiteIntArray*)&g0::tensor_dimension15, 200, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant13))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 0), (TfLiteIntArray*)&g0::tensor_dimension16, 200, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant13))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 400), (TfLiteIntArray*)&g0::tensor_dimension17, 400, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant17))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 0), (TfLiteIntArray*)&g0::tensor_dimension18, 400, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant17))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 400), (TfLiteIntArray*)&g0::tensor_dimension19, 208, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant17))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 0), (TfLiteIntArray*)&g0::tensor_dimension20, 208, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant17))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 208), (TfLiteIntArray*)&g0::tensor_dimension21, 2, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant21))}, },
{ kTfLiteArenaRw, kTfLiteInt8, (int32_t*)(tensor_arena + 0), (TfLiteIntArray*)&g0::tensor_dimension21, 2, {kTfLiteAffineQuantization, const_cast<void*>(static_cast<const void*>(&g0::quant22))}, },
};

#ifndef TF_LITE_STATIC_MEMORY
TfLiteNode tflNodes[11] = {
{ (TfLiteIntArray*)&g0::inputs0, (TfLiteIntArray*)&g0::outputs0, (TfLiteIntArray*)&g0::inputs0, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata0)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs1, (TfLiteIntArray*)&g0::outputs1, (TfLiteIntArray*)&g0::inputs1, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata1)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs2, (TfLiteIntArray*)&g0::outputs2, (TfLiteIntArray*)&g0::inputs2, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata2)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs3, (TfLiteIntArray*)&g0::outputs3, (TfLiteIntArray*)&g0::inputs3, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata3)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs4, (TfLiteIntArray*)&g0::outputs4, (TfLiteIntArray*)&g0::inputs4, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata4)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs5, (TfLiteIntArray*)&g0::outputs5, (TfLiteIntArray*)&g0::inputs5, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata5)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs6, (TfLiteIntArray*)&g0::outputs6, (TfLiteIntArray*)&g0::inputs6, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata6)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs7, (TfLiteIntArray*)&g0::outputs7, (TfLiteIntArray*)&g0::inputs7, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata7)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs8, (TfLiteIntArray*)&g0::outputs8, (TfLiteIntArray*)&g0::inputs8, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata8)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs9, (TfLiteIntArray*)&g0::outputs9, (TfLiteIntArray*)&g0::inputs9, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata9)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs10, (TfLiteIntArray*)&g0::outputs10, (TfLiteIntArray*)&g0::inputs10, nullptr, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata10)), nullptr, 0, },
};
#else
TfLiteNode tflNodes[11] = {
{ (TfLiteIntArray*)&g0::inputs0, (TfLiteIntArray*)&g0::outputs0, (TfLiteIntArray*)&g0::inputs0, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata0)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs1, (TfLiteIntArray*)&g0::outputs1, (TfLiteIntArray*)&g0::inputs1, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata1)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs2, (TfLiteIntArray*)&g0::outputs2, (TfLiteIntArray*)&g0::inputs2, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata2)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs3, (TfLiteIntArray*)&g0::outputs3, (TfLiteIntArray*)&g0::inputs3, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata3)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs4, (TfLiteIntArray*)&g0::outputs4, (TfLiteIntArray*)&g0::inputs4, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata4)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs5, (TfLiteIntArray*)&g0::outputs5, (TfLiteIntArray*)&g0::inputs5, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata5)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs6, (TfLiteIntArray*)&g0::outputs6, (TfLiteIntArray*)&g0::inputs6, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata6)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs7, (TfLiteIntArray*)&g0::outputs7, (TfLiteIntArray*)&g0::inputs7, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata7)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs8, (TfLiteIntArray*)&g0::outputs8, (TfLiteIntArray*)&g0::inputs8, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata8)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs9, (TfLiteIntArray*)&g0::outputs9, (TfLiteIntArray*)&g0::inputs9, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata9)), nullptr, 0, },
{ (TfLiteIntArray*)&g0::inputs10, (TfLiteIntArray*)&g0::outputs10, (TfLiteIntArray*)&g0::inputs10, nullptr, const_cast<void*>(static_cast<const void*>(&g0::opdata10)), nullptr, 0, },
};
#endif

used_operators_e used_ops[] =
{OP_RESHAPE, OP_CONV_2D, OP_RESHAPE, OP_MAX_POOL_2D, OP_RESHAPE, OP_CONV_2D, OP_RESHAPE, OP_MAX_POOL_2D, OP_RESHAPE, OP_FULLY_CONNECTED, OP_SOFTMAX, };


// Indices into tflTensors and tflNodes for subgraphs
const size_t tflTensors_subgraph_index[] = {0, 23, };
const size_t tflNodes_subgraph_index[] = {0, 11, };

// Input/output tensors
static const int in_tensor_indices[] = {
  0, 
};

static const int out_tensor_indices[] = {
  22, 
};


size_t current_subgraph_index = 0;

static void init_tflite_tensor(size_t i, TfLiteTensor *tensor) {
  tensor->type = tensorData[i].type;
  tensor->is_variable = false;

#if defined(EI_CLASSIFIER_ALLOCATION_HEAP)
  tensor->allocation_type = tensorData[i].allocation_type;
#else
  tensor->allocation_type = (tensor_arena <= tensorData[i].data && tensorData[i].data < tensor_arena + kTensorArenaSize) ? kTfLiteArenaRw : kTfLiteMmapRo;
#endif
  tensor->bytes = tensorData[i].bytes;
  tensor->dims = tensorData[i].dims;

#if defined(EI_CLASSIFIER_ALLOCATION_HEAP)
  if(tensor->allocation_type == kTfLiteArenaRw){
    uint8_t* start = (uint8_t*) ((uintptr_t)tensorData[i].data + (uintptr_t) tensor_arena);

    tensor->data.data =  start;
  }
  else {
      tensor->data.data = tensorData[i].data;
  }
#else
  tensor->data.data = tensorData[i].data;
#endif // EI_CLASSIFIER_ALLOCATION_HEAP
  tensor->quantization = tensorData[i].quantization;
  if (tensor->quantization.type == kTfLiteAffineQuantization) {
    TfLiteAffineQuantization const* quant = ((TfLiteAffineQuantization const*)(tensorData[i].quantization.params));
    tensor->params.scale = quant->scale->data[0];
    tensor->params.zero_point = quant->zero_point->data[0];
  }

}

static void init_tflite_eval_tensor(int i, TfLiteEvalTensor *tensor) {

  tensor->type = tensorData[i].type;

  tensor->dims = tensorData[i].dims;

#if defined(EI_CLASSIFIER_ALLOCATION_HEAP)
  auto allocation_type = tensorData[i].allocation_type;
  if(allocation_type == kTfLiteArenaRw) {
    uint8_t* start = (uint8_t*) ((uintptr_t)tensorData[i].data + (uintptr_t) tensor_arena);

    tensor->data.data =  start;
  }
  else {
    tensor->data.data = tensorData[i].data;
  }
#else
  tensor->data.data = tensorData[i].data;
#endif // EI_CLASSIFIER_ALLOCATION_HEAP
}

static void* overflow_buffers[EI_MAX_OVERFLOW_BUFFER_COUNT];
static size_t overflow_buffers_ix = 0;
static void * AllocatePersistentBufferImpl(struct TfLiteContext* ctx,
                                       size_t bytes) {
  void *ptr;
  uint32_t align_bytes = (bytes % 16) ? 16 - (bytes % 16) : 0;

  if (current_location - (bytes + align_bytes) < tensor_boundary) {
    if (overflow_buffers_ix > EI_MAX_OVERFLOW_BUFFER_COUNT - 1) {
      ei_printf("ERR: Failed to allocate persistent buffer of size %d, does not fit in tensor arena and reached EI_MAX_OVERFLOW_BUFFER_COUNT\n",
        (int)bytes);
      return NULL;
    }

    // OK, this will look super weird, but.... we have CMSIS-NN buffers which
    // we cannot calculate beforehand easily.
    ptr = ei_calloc(bytes, 1);
    if (ptr == NULL) {
      ei_printf("ERR: Failed to allocate persistent buffer of size %d\n", (int)bytes);
      return NULL;
    }
    overflow_buffers[overflow_buffers_ix++] = ptr;
    return ptr;
  }

  current_location -= bytes;

  // align to the left aligned boundary of 16 bytes
  current_location -= 15; // for alignment
  current_location += 16 - ((uintptr_t)(current_location) & 15);

  ptr = current_location;
  memset(ptr, 0, bytes);

  return ptr;
}

typedef struct {
  size_t bytes;
  void *ptr;
} scratch_buffer_t;

static scratch_buffer_t scratch_buffers[EI_MAX_SCRATCH_BUFFER_COUNT];
static size_t scratch_buffers_ix = 0;

static TfLiteStatus RequestScratchBufferInArenaImpl(struct TfLiteContext* ctx, size_t bytes,
                                                int* buffer_idx) {
  if (scratch_buffers_ix > EI_MAX_SCRATCH_BUFFER_COUNT - 1) {
    ei_printf("ERR: Failed to allocate scratch buffer of size %d, reached EI_MAX_SCRATCH_BUFFER_COUNT\n",
      (int)bytes);
    return kTfLiteError;
  }

  scratch_buffer_t b;
  b.bytes = bytes;

  b.ptr = AllocatePersistentBufferImpl(ctx, b.bytes);
  if (!b.ptr) {
    ei_printf("ERR: Failed to allocate scratch buffer of size %d\n",
      (int)bytes);
    return kTfLiteError;
  }

  scratch_buffers[scratch_buffers_ix] = b;
  *buffer_idx = scratch_buffers_ix;

  scratch_buffers_ix++;

  return kTfLiteOk;
}

static void* GetScratchBufferImpl(struct TfLiteContext* ctx, int buffer_idx) {
  if (buffer_idx > (int)scratch_buffers_ix) {
    return NULL;
  }
  return scratch_buffers[buffer_idx].ptr;
}

static const uint16_t TENSOR_IX_UNUSED = 0x7FFF;

static void ResetTensors() {
  for (size_t ix = 0; ix < MAX_TFL_TENSOR_COUNT; ix++) {
    tflTensors[ix].index = TENSOR_IX_UNUSED;
  }
  for (size_t ix = 0; ix < MAX_TFL_EVAL_COUNT; ix++) {
    tflEvalTensors[ix].index = TENSOR_IX_UNUSED;
  }
}

static TfLiteTensor* GetTensorImpl(const struct TfLiteContext* context,
                               int tensor_idx) {

  tensor_idx = tflTensors_subgraph_index[current_subgraph_index] + tensor_idx;

  for (size_t ix = 0; ix < MAX_TFL_TENSOR_COUNT; ix++) {
    // already used? OK!
    if (tflTensors[ix].index == tensor_idx) {
      return &tflTensors[ix].tensor;
    }
    // passed all the ones we've used, so end of the list?
    if (tflTensors[ix].index == TENSOR_IX_UNUSED) {
      // init the tensor
      init_tflite_tensor(tensor_idx, &tflTensors[ix].tensor);
      tflTensors[ix].index = tensor_idx;
      return &tflTensors[ix].tensor;
    }
  }

  ei_printf("ERR: GetTensor called beyond MAX_TFL_TENSOR_COUNT (%d)\n", MAX_TFL_TENSOR_COUNT);
  return nullptr;
}

static TfLiteEvalTensor* GetEvalTensorImpl(const struct TfLiteContext* context,
                                       int tensor_idx) {

  tensor_idx = tflTensors_subgraph_index[current_subgraph_index] + tensor_idx;

  for (size_t ix = 0; ix < MAX_TFL_EVAL_COUNT; ix++) {
    // already used? OK!
    if (tflEvalTensors[ix].index == tensor_idx) {
      return &tflEvalTensors[ix].tensor;
    }
    // passed all the ones we've used, so end of the list?
    if (tflEvalTensors[ix].index == TENSOR_IX_UNUSED) {
      // init the tensor
      init_tflite_eval_tensor(tensor_idx, &tflEvalTensors[ix].tensor);
      tflEvalTensors[ix].index = tensor_idx;
      return &tflEvalTensors[ix].tensor;
    }
  }

  ei_printf("ERR: GetTensor called beyond MAX_TFL_EVAL_COUNT (%d)\n", (int)MAX_TFL_EVAL_COUNT);
  return nullptr;
}

class EonMicroContext : public MicroContext {
 public:
 
  EonMicroContext(): MicroContext(nullptr, nullptr, nullptr) { }

  void* AllocatePersistentBuffer(size_t bytes) {
    return AllocatePersistentBufferImpl(nullptr, bytes);
  }

  TfLiteStatus RequestScratchBufferInArena(size_t bytes,
                                           int* buffer_index) {
  return RequestScratchBufferInArenaImpl(nullptr, bytes, buffer_index);
  }

  void* GetScratchBuffer(int buffer_index) {
    return GetScratchBufferImpl(nullptr, buffer_index);
  }
 
  TfLiteTensor* AllocateTempTfLiteTensor(int tensor_index) {
    return GetTensorImpl(nullptr, tensor_index);
  }

  void DeallocateTempTfLiteTensor(TfLiteTensor* tensor) {
    return;
  }

  bool IsAllTempTfLiteTensorDeallocated() {
    return true;
  }

  TfLiteEvalTensor* GetEvalTensor(int tensor_index) {
    return GetEvalTensorImpl(nullptr, tensor_index);
  }

};


} // namespace

TfLiteStatus tflite_learn_3_init( void*(*alloc_fnc)(size_t,size_t) ) {
#ifdef EI_CLASSIFIER_ALLOCATION_HEAP
  tensor_arena = (uint8_t*) alloc_fnc(16, kTensorArenaSize);
  if (!tensor_arena) {
    ei_printf("ERR: failed to allocate tensor arena\n");
    return kTfLiteError;
  }
#else
  memset(tensor_arena, 0, kTensorArenaSize);
#endif
  tensor_boundary = tensor_arena;
  current_location = tensor_arena + kTensorArenaSize;

  EonMicroContext micro_context_;
  
  // Set microcontext as the context ptr
  ctx.impl_ = static_cast<void*>(&micro_context_);
  // Setup tflitecontext functions
  ctx.AllocatePersistentBuffer = &AllocatePersistentBufferImpl;
  ctx.RequestScratchBufferInArena = &RequestScratchBufferInArenaImpl;
  ctx.GetScratchBuffer = &GetScratchBufferImpl;
  ctx.GetTensor = &GetTensorImpl;
  ctx.GetEvalTensor = &GetEvalTensorImpl;
  ctx.ReportError = &MicroContextReportOpError;

  ctx.tensors_size = 23;
  for (size_t i = 0; i < 23; ++i) {
    TfLiteTensor tensor;
    init_tflite_tensor(i, &tensor);
    if (tensor.allocation_type == kTfLiteArenaRw) {
      auto data_end_ptr = (uint8_t*)tensor.data.data + tensorData[i].bytes;
      if (data_end_ptr > tensor_boundary) {
        tensor_boundary = data_end_ptr;
      }
    }
  }

  if (tensor_boundary > current_location /* end of arena size */) {
    ei_printf("ERR: tensor arena is too small, does not fit model - even without scratch buffers\n");
    return kTfLiteError;
  }

  registrations[OP_RESHAPE] = Register_RESHAPE();
  registrations[OP_CONV_2D] = Register_CONV_2D();
  registrations[OP_MAX_POOL_2D] = Register_MAX_POOL_2D();
  registrations[OP_FULLY_CONNECTED] = Register_FULLY_CONNECTED();
  registrations[OP_SOFTMAX] = Register_SOFTMAX();

  for (size_t g = 0; g < 1; ++g) {
    current_subgraph_index = g;
    for(size_t i = tflNodes_subgraph_index[g]; i < tflNodes_subgraph_index[g+1]; ++i) {
      if (registrations[used_ops[i]].init) {
        tflNodes[i].user_data = registrations[used_ops[i]].init(&ctx, (const char*)tflNodes[i].builtin_data, 0);
      }
    }
  }
  current_subgraph_index = 0;

  for(size_t g = 0; g < 1; ++g) {
    current_subgraph_index = g;
    for(size_t i = tflNodes_subgraph_index[g]; i < tflNodes_subgraph_index[g+1]; ++i) {
      if (registrations[used_ops[i]].prepare) {
        ResetTensors();
        TfLiteStatus status = registrations[used_ops[i]].prepare(&ctx, &tflNodes[i]);
        if (status != kTfLiteOk) {
          return status;
        }
      }
    }
  }
  current_subgraph_index = 0;

  return kTfLiteOk;
}

TfLiteStatus tflite_learn_3_input(int index, TfLiteTensor *tensor) {
  init_tflite_tensor(in_tensor_indices[index], tensor);
  return kTfLiteOk;
}

TfLiteStatus tflite_learn_3_output(int index, TfLiteTensor *tensor) {
  init_tflite_tensor(out_tensor_indices[index], tensor);
  return kTfLiteOk;
}

TfLiteStatus tflite_learn_3_invoke() {
  for (size_t i = 0; i < 11; ++i) {
    ResetTensors();

    TfLiteStatus status = registrations[used_ops[i]].invoke(&ctx, &tflNodes[i]);

#if EI_CLASSIFIER_PRINT_STATE
    ei_printf("layer %lu\n", i);
    ei_printf("    inputs:\n");
    for (size_t ix = 0; ix < tflNodes[i].inputs->size; ix++) {
      auto d = tensorData[tflNodes[i].inputs->data[ix]];

      size_t data_ptr = (size_t)d.data;

      if (d.allocation_type == kTfLiteArenaRw) {
        data_ptr = (size_t)tensor_arena + data_ptr;
      }

      if (d.type == TfLiteType::kTfLiteInt8) {
        int8_t* data = (int8_t*)data_ptr;
        ei_printf("        %lu (%zu bytes, ptr=%p, alloc_type=%d, type=%d): ", ix, d.bytes, data, (int)d.allocation_type, (int)d.type);
        for (size_t jx = 0; jx < d.bytes; jx++) {
          ei_printf("%d ", data[jx]);
        }
      }
      else {
        float* data = (float*)data_ptr;
        ei_printf("        %lu (%zu bytes, ptr=%p, alloc_type=%d, type=%d): ", ix, d.bytes, data, (int)d.allocation_type, (int)d.type);
        for (size_t jx = 0; jx < d.bytes / 4; jx++) {
          ei_printf("%f ", data[jx]);
        }
      }
      ei_printf("\n");
    }
    ei_printf("\n");

    ei_printf("    outputs:\n");
    for (size_t ix = 0; ix < tflNodes[i].outputs->size; ix++) {
      auto d = tensorData[tflNodes[i].outputs->data[ix]];

      size_t data_ptr = (size_t)d.data;

      if (d.allocation_type == kTfLiteArenaRw) {
        data_ptr = (size_t)tensor_arena + data_ptr;
      }

      if (d.type == TfLiteType::kTfLiteInt8) {
        int8_t* data = (int8_t*)data_ptr;
        ei_printf("        %lu (%zu bytes, ptr=%p, alloc_type=%d, type=%d): ", ix, d.bytes, data, (int)d.allocation_type, (int)d.type);
        for (size_t jx = 0; jx < d.bytes; jx++) {
          ei_printf("%d ", data[jx]);
        }
      }
      else {
        float* data = (float*)data_ptr;
        ei_printf("        %lu (%zu bytes, ptr=%p, alloc_type=%d, type=%d): ", ix, d.bytes, data, (int)d.allocation_type, (int)d.type);
        for (size_t jx = 0; jx < d.bytes / 4; jx++) {
          ei_printf("%f ", data[jx]);
        }
      }
      ei_printf("\n");
    }
    ei_printf("\n");
#endif // EI_CLASSIFIER_PRINT_STATE

    if (status != kTfLiteOk) {
      return status;
    }
  }
  return kTfLiteOk;
}

TfLiteStatus tflite_learn_3_reset( void (*free_fnc)(void* ptr) ) {
#ifdef EI_CLASSIFIER_ALLOCATION_HEAP
  free_fnc(tensor_arena);
#endif

  // scratch buffers are allocated within the arena, so just reset the counter so memory can be reused
  scratch_buffers_ix = 0;

  // overflow buffers are on the heap, so free them first
  for (size_t ix = 0; ix < overflow_buffers_ix; ix++) {
    ei_free(overflow_buffers[ix]);
  }
  overflow_buffers_ix = 0;
  return kTfLiteOk;
}
