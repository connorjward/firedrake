window.BENCHMARK_DATA = {
  "lastUpdate": 1651686299549,
  "repoUrl": "https://github.com/connorjward/firedrake",
  "entries": {
    "Python Benchmark with pytest-benchmark": [
      {
        "commit": {
          "author": {
            "email": "c.ward20@imperial.ac.uk",
            "name": "Connor Ward",
            "username": "connorjward"
          },
          "committer": {
            "email": "c.ward20@imperial.ac.uk",
            "name": "Connor Ward",
            "username": "connorjward"
          },
          "distinct": true,
          "id": "4e14b88154da77d88d68429c12feb0bb17c92496",
          "message": "fix",
          "timestamp": "2022-04-29T19:22:38+01:00",
          "tree_id": "bec9cfe35be2c94a36ef34570e945985e0b8d36f",
          "url": "https://github.com/connorjward/firedrake/commit/4e14b88154da77d88d68429c12feb0bb17c92496"
        },
        "date": 1651256589967,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_demo.py::test_my_stuff1",
            "value": 16575.777040989353,
            "unit": "iter/sec",
            "range": "stddev: 0.000002642002495214567",
            "extra": "mean: 60.32899679617754 usec\nrounds: 11549"
          },
          {
            "name": "benchmarks/test_demo.py::test_my_stuff2",
            "value": 467.8594163951414,
            "unit": "iter/sec",
            "range": "stddev: 0.000024595786234612508",
            "extra": "mean: 2.137394193548574 msec\nrounds: 465"
          },
          {
            "name": "benchmarks/test_demo.py::test_my_stuff3",
            "value": 1159.9730082363458,
            "unit": "iter/sec",
            "range": "stddev: 0.0000043971856640940085",
            "extra": "mean: 862.0890252613955 usec\nrounds: 1148"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "c.ward20@imperial.ac.uk",
            "name": "Connor Ward",
            "username": "connorjward"
          },
          "committer": {
            "email": "c.ward20@imperial.ac.uk",
            "name": "Connor Ward",
            "username": "connorjward"
          },
          "distinct": true,
          "id": "88cec3b5f7b8b5117ef96b113755eb209bc5b77c",
          "message": "Modify test benchmark values",
          "timestamp": "2022-04-29T19:30:25+01:00",
          "tree_id": "2f7bf0257a13547bcbcd7c608249e80d106a6ae5",
          "url": "https://github.com/connorjward/firedrake/commit/88cec3b5f7b8b5117ef96b113755eb209bc5b77c"
        },
        "date": 1651257057721,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_demo.py::test_my_stuff1",
            "value": 920.7821992370436,
            "unit": "iter/sec",
            "range": "stddev: 0.0000624344990763387",
            "extra": "mean: 1.0860331583610063 msec\nrounds: 903"
          },
          {
            "name": "benchmarks/test_demo.py::test_my_stuff2",
            "value": 3706.172045458424,
            "unit": "iter/sec",
            "range": "stddev: 0.000021358339939734844",
            "extra": "mean: 269.82017772904226 usec\nrounds: 3646"
          },
          {
            "name": "benchmarks/test_demo.py::test_my_stuff3",
            "value": 6667.370816988141,
            "unit": "iter/sec",
            "range": "stddev: 0.00005081687206199228",
            "extra": "mean: 149.98415829100847 usec\nrounds: 6109"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "c.ward20@imperial.ac.uk",
            "name": "Connor Ward",
            "username": "connorjward"
          },
          "committer": {
            "email": "c.ward20@imperial.ac.uk",
            "name": "Connor Ward",
            "username": "connorjward"
          },
          "distinct": true,
          "id": "35cfb90684a87de3eee34f2ca6b1403bd0cd341c",
          "message": "have i fixed it? v6",
          "timestamp": "2022-05-04T16:42:04+01:00",
          "tree_id": "beb6ce132cdba879b22f9d2e9c5744790bcadbed",
          "url": "https://github.com/connorjward/firedrake/commit/35cfb90684a87de3eee34f2ca6b1403bd0cd341c"
        },
        "date": 1651682041176,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/regression/test_stokes_mini.py::test_stokes_mini_benchmark[aij]",
            "value": 0.8670138778184963,
            "unit": "iter/sec",
            "range": "stddev: 0.027105711553011207",
            "extra": "mean: 1.1533840755999336 sec\nrounds: 5"
          },
          {
            "name": "tests/regression/test_stokes_mini.py::test_stokes_mini_benchmark[nest]",
            "value": 0.8729023775282085,
            "unit": "iter/sec",
            "range": "stddev: 0.05890813452095926",
            "extra": "mean: 1.1456034784000622 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "c.ward20@imperial.ac.uk",
            "name": "Connor Ward",
            "username": "connorjward"
          },
          "committer": {
            "email": "c.ward20@imperial.ac.uk",
            "name": "Connor Ward",
            "username": "connorjward"
          },
          "distinct": true,
          "id": "4bbdca140a86567e173bc0b1ae5e38f092b38b6c",
          "message": "test everything please",
          "timestamp": "2022-05-04T17:38:42+01:00",
          "tree_id": "51cb84b173cd4a021a567311039c9c8cb5a56cdb",
          "url": "https://github.com/connorjward/firedrake/commit/4bbdca140a86567e173bc0b1ae5e38f092b38b6c"
        },
        "date": 1651686298584,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/regression/test_stokes_mini.py::test_stokes_mini_benchmark[aij]",
            "value": 0.6715255494108534,
            "unit": "iter/sec",
            "range": "stddev: 0.02391001560706187",
            "extra": "mean: 1.4891466168000989 sec\nrounds: 5"
          },
          {
            "name": "tests/regression/test_stokes_mini.py::test_stokes_mini_benchmark[nest]",
            "value": 0.6531532044139564,
            "unit": "iter/sec",
            "range": "stddev: 0.02685047281182208",
            "extra": "mean: 1.531034362599894 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}